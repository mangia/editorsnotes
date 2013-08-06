function editTextBlock($contentElement, opts) {
  var that = this
    , options = opts || {}
    , content = opts.content || $contentElement.html()
    , id = opts.id || Math.floor(Math.random() * 100000)
    , $container = opts.container || $contentElement.parent()
    , $textarea
    , taHeight
    , toolbar
    , editor

  taHeight = (function (h) {
    return (h < 380 ? h : 380) + 100;
  })($contentElement.innerHeight());

  $textarea = $('<textarea>')
    .attr('id', id)
    .css({ 'margin-bottom': '0', 'width': '99%', 'height': taHeight })
    .val(content)
    .insertAfter($contentElement);

  $container.css({ 'min-height': taHeight + 8 });

  $contentElement.hide();

  toolbar = $('#note-section-toolbar').clone()
    .attr('id', id + '-toolbar')
    .insertBefore($textarea)
    .show();

  editor = new wysihtml5.Editor(id, _.extend({
    toolbar: id + '-toolbar'
  }, EditorsNotes.wysihtml5BaseOpts));

  editor.on('load', function () { $container.css({ 'min-height': ''}) });

  return editor;
}

// The toolbar controlling adding new note sections & saving the collection
// of sections.
EditorsNotes.Views['AddSectionToolbar'] = Backbone.View.extend({
  initialize: function (opts) {
    var that = this;

    this.note = opts.note;
    this.render();

    this.$loader = this.$('img').css({
      'display': 'none',
      'position': 'relative',
      'float': 'right',
      'top': '6px',
      'left': '-10px'
    });
    this.$saveMsg = this.$('span').css({
      'display': 'none',
      'float': 'right',
      'font-size': '15px',
      'margin-top': '4px',
      'margin-right': '5px'
    });

    this.note.once('sync', function () {
      that.listenTo(that.note, 'request', that.showLoader);
      that.listenTo(that.note.sections, 'request', that.showLoader);
    });
  },
  events: { 'click .add-section': 'addSection' },
  render: function () {
    this.$el.attr('id', 'citation-edit-bar');

    // Coulda been a template but there's no variables so...
    // (TODO get this outta here)
    this.$el.append(''
      + '<h4>Add section: </h4>'
      + '<a class="add-section" data-section-type="citation">Citation</a>'
      + '<a class="add-section" data-section-type="text">Text</a>'
      + '<a class="add-section" data-section-type="note_reference">Reference to a note</a>'
      + '<span>All changes saved.</span>'
      + '<img style="display: none; float: right;" src="/static/style/icons/ajax-loader.gif">')
  },

  showLoader: function (model, xhr) {
    var $msg = this.$saveMsg.hide()
      , $loader = this.$loader.show()

    xhr.always(function () {
      $loader.hide();
      $msg.show()
        .css('opacity', 1)
        .animate({ 'opacity': 1 })
        .animate({ 'opacity': 0})
    });

  },

  saveSections: function () {
    var that = this
      , sections
      , promises

    this.showLoading();

    sections = this.note.sections.filter(function (s) { return s.isDirty });
    promises = sections.map(function (s) { return s.save() });

    $.when.apply($, promises).done(function () {
      sections.forEach(function (s) { s.isDirty = false });
      that.note.sections.trigger('reorder');
      that.disableButton.call(that);
    });
  },

  addSection: function (e) {
    var sectionType = $(e.currentTarget).data('sectionType')
      , idx = 0

    e.preventDefault();

    // TODO: idx is always 0 right now, so sections are added at the top of
    // the list, but that can be changed.
    //
    // Sort is false because sections are ordered by the index of their ID in
    // the note's section_ordering field. Since this new section does not yet
    // have an ID, it can't be sorted.
    //
    this.note.sections.add({ 'section_type': sectionType }, { at: idx, sort: false });
  }
});

EditorsNotes.Views['NoteSectionList'] = Backbone.View.extend({
  initialize: function (options) {
    var that = this;

    this.note = this.model;
    this.project = this.project;

    // Keep track of all the note sections views internally
    this._sectionViews = [];

    // Instantiate the toolbar to add/save sections
    this.addView = new EditorsNotes.Views.AddSectionToolbar({ note: this.note });
    this.addView.$el.insertBefore(this.$el);

    // Listen to all appropriate section events.
    this.listenTo(this.note.sections, 'add', this.addSection);
    this.listenTo(this.note.sections, 'remove', this.removeSection);
    this.listenTo(this.note.sections, 'set', this.render);

    this.listenTo(this.note.sections, 'deactivate', this.deactivateSections);
    this.listenTo(this.note.sections, 'sync', this.saveOrder);
    this.listenTo(this.note.sections, 'reorder', this.saveOrder);
  },

  render: function () {
    $('body').addClass('editing');
    this.$el.empty();
    this._rendered = true;
    this._sectionViews.forEach(function (sectionView) {
      this.$el.append(sectionView.el);
    }, this);

    this.initSort();
  },

  initSort: function () {
    var that = this;
    this.$el.sortable({
      placeholder: 'section-placeholder',
      cancel: 'input,textarea,button,select,option,.note-section-edit-active',
      cursor: 'pointer',
      cursorAt: { 'left': 200, 'top': 20 },
      helper: function (event, item) {
        return $(item).clone().addClass('active').css({
          'max-height': '120px',
          'border': 'none',
          'opacity': .75
        });
      },
      start: function (event, ui) {
        that.deactivateSections();
        $(this).addClass('sort-active');
        ui.item.hide();
        that.$el.sortable('refreshPositions');
      },
      stop: function () {
        $(this).removeClass('sort-active');
      },
      update: function (event, ui) {
        ui.item.show();
        that.saveOrder.call(that);
      }
    });
  },

  addSection: function (section) {

    var idx = section.collection.indexOf(section)
      , SectionView = EditorsNotes.Views['sections/' + section.get('section_type')]
      , view = new SectionView({ model: section })
      , target

    view.$el.data('sectionCID', view.model.cid);
    this._sectionViews.splice(idx, 0, view);

    if (!this._rendered) return;

    if (idx === 0) {
      this.$el.prepend(view.el);
    } else {
      target = this.$el.children()[idx - 1];
      view.$el.insertAfter(target);
    }

    if (section.isNew()) view.$el.trigger('click');
  },

  removeSection: function (section) {
    var that = this
      , sectionOrdering = this.note.get('section_ordering')
      , sectionViews = _(that._sectionViews)
      , viewToRemove

    viewToRemove = sectionViews.find(function (view) {
      return view.model === section
    });

    this._sectionViews = sectionViews.without(viewToRemove);

    sectionOrdering.pop(section.id);
    this.note.set('section_ordering', sectionOrdering);
  },

  deactivateSections: function (e) {
    var that = this;
    this._sectionViews.forEach(function (view) {
      view.deactivate.call(view);
    });
  },

  saveOrder: function () {
    var that = this
      , noteOrdering = this.note.get('section_ordering')
      , renderedOrder = []
      , viewOrdering = []
      , renderedOrder

    renderedOrder = this.$el.children('.note-section').map(function (idx, el) {
      return $(el).data('sectionCID');
    }).toArray();

    this._sectionViews.sort(function (a, b) {
      var idxa = renderedOrder.indexOf(a.model.cid)
        , idxb = renderedOrder.indexOf(b.model.cid)

      return idxa > idxb;
    });

    this._sectionViews.forEach(function (view) {
      if (view.model.id) viewOrdering.push(view.model.id);
    });

    if (noteOrdering.join('') !== viewOrdering.join('')) {
      this.note.set('section_ordering', viewOrdering);
      this.note.save();
    }
  }

});

/*
 * Base view for all note sections. Children must define the following methods:
 *
 * `isEmpty`
 */

EditorsNotes.Views['NoteSection'] = Backbone.View.extend({
  tagName: 'div',
  className: 'note-section',
  isActive: false,

  events: { 'click': 'edit' },

  initialize: function () {
    this.render();
    this.$el.addClass('note-section-' + this.model.get('section_type'));
  },

  render: function () {
    var that = this
      , sectionType = this.model.get('section_type')
      , template = EditorsNotes.Templates['note_sections/' + sectionType]

    this.$el.html( template({ns: that.model.toJSON()}) );
    this.afterRender && this.afterRender.call(this);
  },

  edit: function () {
    var that = this
      , html

    if (this.isActive) return;

    this.model.collection.trigger('deactivate');

    this.isActive = true;
    this.$el.addClass('note-section-edit-active');
    this.editTextContent();

    html = ''
      + '<div class="edit-row row">'
        + '<a class="btn btn-primary save-section pull-right">Save</a>'
        + '<a class="btn btn-danger delete-section">Delete section</a>'
      + '</div>'

    $(html)
      .appendTo(this.$el)
      .on('click .btn', function (e) {
        var deleteSection = $(e.target).hasClass('delete-section');
        setTimeout(function () { that.deactivate.call(that, deleteSection); }, 10);
      });

    return;
  },

  deactivate: function (deleteModel) {
    var collection;

    if (!this.isActive) return;

    this.isActive = false;
    this.$el.removeClass('note-section-edit-active');
    this.deactivateTextContent();

    if (this.isEmpty() || deleteModel) {
      collection = this.model.collection
      this.remove();
      this.model.destroy({
        success: function (model) {
          collection.remove(model);
          collection.trigger('removeEmpty');
        }
      });
    }

    this.model.save();
    return;
  },

  editTextContent: function () {
    var that = this
      , content = this.model.get('content')
      , $content = this.$('.note-section-text-content')

    this.contentEditor = editTextBlock($content, {
      id: 'edit-section-' + this.model.cid,
      content: this.model.get('content'),
      container: this.$el
    });

    this.contentEditor.on('input', function () {
      that.model.set('content', that.contentEditor.getValue().replace('<br>', '<br/>'));
    });
  },

  deactivateTextContent: function (saveModelChanges) {
    var saveChanges = saveModelChanges === undefined ? true : !!saveChangesOpt
      , contentValue = this.contentEditor.getValue().replace('<br>', '<br/>')
      , toRemove = [
        'iframe.wysihtml5-sandbox',
        'input[name="_wysihtml5_mode"]',
        '.btn-toolbar',
        '.edit-row',
        'textarea'
      ]

    if (saveChanges) {
      this.model.set('content', contentValue || null);
      this.$('.note-section-text-content').html(contentValue);
    }
    this.$('.note-section-text-content').show();

    this.$(toRemove.join(',')).remove();
  }
  
});

EditorsNotes.Views['sections/citation'] = EditorsNotes.Views.NoteSection.extend({
  afterRender: function () {
    var that = this
      , addDocumentView
      , $documentContainer

    if (!this.model.isNew()) return;

    selectDocumentView = new EditorsNotes.Views.SelectDocument({ project: this.model.project });
    $documentContainer = this.$('.citation-document').html(selectDocumentView.el);

    this.listenToOnce(selectDocumentView, 'documentSelected', function (doc) {
      $documentContainer.html(doc.get('description'));
      that.model.set('document_description', doc.get('description'));
      that.model.set('document', doc.url());
      selectDocumentView.remove();
    });

  },
  isEmpty: function () { return !this.model.has('document') }
});

EditorsNotes.Views['sections/note_reference'] = EditorsNotes.Views.NoteSection.extend({
  afterRender: function () {
    var that = this
      , addNoteView
      , $noteContainer

    if (!this.model.isNew()) return;

    addNoteView = new EditorsNotes.Views.SelectNote({ project: this.model.project });
    $noteContainer = this.$('.note-reference-note-container')
      .html(addNoteView.el);

    this.listenToOnce(addNoteView, 'noteSelected', function (note) {
      $noteContainer.html(note.get('title'));
      that.model.set('note_reference', note.url());
      that.model.set('note_reference_title', note.get('title'));
      addNoteView.remove();
    });
  },
  isEmpty: function () { return !this.model.has('note_reference') }
});

EditorsNotes.Views['sections/text'] = EditorsNotes.Views.NoteSection.extend({
  isEmpty: function () { return !this.model.get('content') }
})

/*
 * Base view for selecting items. Includes an autocomplete input and a button
 * to launch a modal for adding an item inline. Inheriting views must define
 * an `addItem` method to handle creating & rendering that modal.
 *
 * Options:
 *    project (required): slug of the project currently being worked on
 *    autocompleteopts: object defining settings for the autocomplete input
 */
EditorsNotes.Views['SelectItem'] = Backbone.View.extend({
  events: {
    'click .add-new-object': 'addItem'
  },
  initialize: function (options) {
    var that = this
      , url

    this.project = options.project;
    url = this.autocompleteURL.call(this)

    this._autocompleteopts = _.extend({
      select: that.selectItem.bind(that),
      appendTo: '#note-sections',
      minLength: 2,
      source: function (request, response) {
        $.getJSON(url, {'q': request.term}, function (data) {
          response(data.results.map(function (item) {
            item.label = item[that.labelAttr || 'title'];
            return item;
          }));
        });
      },
    }, that.autocompleteopts || {})

    this.render();
  },
  render: function () {
    var that = this
      , $input

    this.$el.html(EditorsNotes.Templates.add_or_select_item({type: that.type}));

    $input = this.$('input');
    $input.autocomplete(that._autocompleteopts)
      .data('autocomplete')._renderItem = function (ul, item) {
        return $('<li>')
          .data('item.autocomplete', item)
          .append('<a>' + item.label + '</a>')
          .appendTo(ul)
      }
  }
});

EditorsNotes.Views['SelectDocument'] =  EditorsNotes.Views.SelectItem.extend({
  type: 'document',
  labelAttr: 'description',
  autocompleteURL: function () { return this.project.url() + 'documents/' },

  selectItem: function (event, ui) {
    this.trigger('documentSelected', this.project.documents.add(ui.item).get(ui.item.id));
  },

  addItem: function (e) {
    var that = this
      , addView = new EditorsNotes.Views.AddDocument({ project: this.project });

    e.preventDefault();

    this.listenTo(addView.model, 'sync', function (item) {
      that.trigger('documentSelected', item);
    });
    addView.$el.appendTo('body').modal();
  }
});

EditorsNotes.Views['SelectNote'] = EditorsNotes.Views.SelectItem.extend({
  type: 'note',
  labelAttr: 'title',
  autocompleteURL: function () { return this.project.url() + 'notes/'; },

  selectItem: function (event, ui) {
    this.trigger('noteSelected', this.project.notes.add(ui.item).get(ui.item.id));
  },

  addItem: function (e) {
    var that = this
      , addView = new EditorsNotes.Views.AddNote({ project: this.project });

    e.preventDefault();

    this.listenTo(addView.model, 'sync', function (item) {
      that.trigger('noteSelected', item);
    });
    addView.$el.appendTo('body').modal();
  }
});


/*
 * Base view for all views adding items in a modal
 *
 * Must create saveItem method
 *
 * options:
 *    height
 *    minHeight
 *    width
 */
EditorsNotes.Views['AddItem'] = Backbone.View.extend({
  renderModal: function () {
    var that = this
      , widget
      , $loader

    widget = EditorsNotes.Templates.add_item_modal({
      type: that.itemType,
      textarea: !!that.textarea
    });

    this.$el.html(widget).addClass('modal');
    $loader = this.$('.loader-icon');

    this.$el
      .on('ajaxStart', function () { $loader.show(); })
      .on('ajaxStop', function () { $loader.hide(); })
      .on('hidden', that.remove.bind(that))
      .on('shown', that.setModalSize.bind(that))
      .on('click', '.btn-save-item', that.saveItem.bind(that));
  },

  setModalSize: function () {
    var that = this
      , $w = $(window)
      , modalHeight
      , bodyHeight
      , modalPosition = {
        'my': 'top',
        'at': 'top',
        'of': $w,
        'collision': 'none',
        'offset': '0 20'
      }

    modalHeight = this.options.height || (function () {
      var windowHeight = $w.height() - 50
        , minHeight = that.options.minHeight || 500

      return windowHeight > minHeight ? windowHeight : minHeight;
    })();

    bodyHeight = modalHeight
      - this.$('.modal-header').innerHeight()
      - this.$('.modal-footer').innerHeight()
      - (function (b) {
          var ptop = parseInt(b.css('padding-top'))
            , pbot = parseInt(b.css('padding-bottom'));
          return ptop + pbot;
        })(this.$('.modal-body'))
      - 2; // border

    this.$el.css({
      position: 'absolute',
      width: this.options.width || 840,
      height: modalHeight
    }).position(modalPosition).position(modalPosition);

    this.$('.modal-body').css({
      'height': bodyHeight,
      'max-height': bodyHeight
    });

  }
});

EditorsNotes.Views['AddDocument'] = EditorsNotes.Views.AddItem.extend({
  itemType: 'document',
  textarea: true,
  initialize: function (options) {
    this.model = options.project.documents.add({}, {at: 0}).at(0);
    this.render();
    this.$('.modal-body').append('<div class="add-document-zotero-data">');
    this.zotero_view = new EditorsNotes.Views.EditZoteroInformation({
      el: this.$('.add-document-zotero-data')
    });
  },

  render: function () {
    var that = this;

    this.renderModal();
    this.$el.on('hidden', function () {
      if (that.model.isNew()) that.model.destroy();
    });
  },

  saveItem: function (e) {
    var that = this
      , data = { description: this.$('.item-text-main').val() }
      , zotero_data = this.zotero_view.getZoteroData();

    e.preventDefault();

    if (!_.isEmpty(zotero_data)) {
      data.zotero_data = JSON.stringify(zotero_data);
    }

    this.model.set(data);
    this.model.save(data, {
      success: function () { that.$el.modal('hide') }
    });

  }
});

EditorsNotes.Views['AddNote'] = EditorsNotes.Views.AddItem.extend({
  itemType: 'note',
  initialize: function (options) {
    this.model = options.project.notes.add({}, {at: 0}).at(0);
    this.render();

    // TODO: assigned users & licensing
  },

  render: function () {
    var that = this;

    this.renderModal();

    this.$('.modal-body')
      .prepend('<h5>Title</h5>')
      .append(''
        + '<h5>Description</h5>'
        + '<textarea class="add-note-description" style="width: 98%; height: 80px;"></textarea>');
    this.$el.on('hidden', function () {
      if (that.model.isNew()) that.model.destroy();
    });
  },

  saveItem: function () {
    var that = this
      , data = {
        title: this.$('.item-text-main').val(),
        content: this.$('.add-note-description').val()
      }

    this.model.set(data);
    this.model.save(data, {
      success: function () { that.$el.modal('hide') }
    });
  }
});

EditorsNotes.Views['EditZoteroInformation'] = Backbone.View.extend({
  events: {
    'change .item-type-select': function (e) {
      this.renderZoteroForm(e.currentTarget.value);
    },
    'click .common-item-types li': function (e) {
      e.preventDefault();
      this.renderZoteroForm($('a', e.currentTarget).data('item-type'));
    },
    'click .add-creator': 'addCreator',
    'click .remove-creator': 'removeCreator',
    'input .zotero-entry': 'sendZoteroData',
  },

  initialize: function () {
    var that = this

    this.citeprocWorker = new Worker('/static/function/citeproc-worker.js');
    this.citeprocWorker.addEventListener('message', function (e) {
      that.trigger('updateCitation', e.data.citation);
    });
    this.on('updateCitation', this.updateCitation);

    this.render();

    $.getJSON('/api/document/itemtypes/')
      .done(function (itemTypes) {
        var select = EditorsNotes.Templates['zotero/item_type_select'](itemTypes);
        that.$el.html('<hr />' + select);
        that.$('select').prop('selectedIndex', -1);
      })
      .error(function () {
        console.error('Could not fetch item types from server.');
      });

  },

  renderZoteroForm: function (itemType) {
    var that = this
      , $input = this.$('input').hide()

    $.get('/api/document/template/?itemType=' + itemType)
      .done(function (template) {
        var $template = $(template).filter('#zotero-information-edit');
        that.$el
          .html('<hr />' + $template.html())
          .find('.zotero-entry-delete').remove();
      })
      .fail(function () {
        alert('Could not retrieve template');
        $input.show()
      });
  },

  addCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-creator')
      , $newCreator = $creator.clone()

    e.preventDefault();

    $newCreator.find('textarea').val('');
    $newCreator.insertAfter($creator);

  },

  removeCreator: function (e) {
    var $creator = $(e.currentTarget).closest('.zotero-creator')

    e.preventDefault();

    if ($creator.siblings('.zotero-creator').length) {
      $creator.remove();
    } else {
      $creator.find('textarea').val('');
    }
  },

  getZoteroData: function () {
    var that = this;
    return EditorsNotes.zotero.zoteroFormToObject(that.$el);
  },

  sendZoteroData: function () {
    var zoteroData = this.getZoteroData();
    this.citeprocWorker.postMessage({zotero_data: zoteroData});
  },

  updateCitation: function (citation) { $('.item-text-main').val(citation) }

});
