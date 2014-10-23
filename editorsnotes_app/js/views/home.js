"use strict";

var Backbone = require('../backbone')

module.exports = Backbone.View.extend({
  initialize: function () {
    this.render();
  },
  render: function () {
    var template = require('../templates/dashboard.html');
    this.$el.html(template({ user: this.model.toJSON() }));
  }
});
