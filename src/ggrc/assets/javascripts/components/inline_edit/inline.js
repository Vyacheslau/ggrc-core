/*!
    Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: ivan@reciprocitylabs.com
    Maintained By: ivan@reciprocitylabs.com
*/

(function (can, $) {
  'use strict';

  GGRC.Components('inlineEdit', {
    tag: 'inline-edit',
    template: can.view(
      GGRC.mustache_path +
      '/components/inline_edit/inline.mustache'
    ),
    scope: {
      instance: null,
      type: '@',
      caId: null,
      property: '@',
      value: null,
      values: null,
      isSaving: false,
      context: {
        isEdit: false,
        value: null,
        values: null
      },
      enableEdit: function (ctx, el, ev) {
        ev.preventDefault();
        this.attr('context.isEdit', true);
      },
      onCancel: function (ctx, el, ev) {
        ev.preventDefault();
        this.attr('context.isEdit', false);
        this.attr('context.value', this.attr('_value'));
      },
      onSave: function (ctx, el, ev) {
        var caid = this.attr('caId');
        var property = this.attr('property');
        var instance = this.attr('instance');
        var oldValue = this.attr('value');
        var value = this.attr('context.value');
        var type = this.attr('type');

        ev.preventDefault();
        this.attr('context.isEdit', false);
        if (oldValue === value) {
          return;
        }

        this.attr('_value', value);
        this.attr('isSaving', true);
        instance.refresh().then(function () {
          if (this.attr('caId')) {
            if (type === 'checkbox') {
              value = value ? 1 : 0;
            }
            if (type === 'person') {
              value = value ? ('Person:' + value.id) : value;
            }
            if (type === 'dropdown') {
              if (value && value === '') {
                value = undefined;
              }
            }
            instance.attr('custom_attributes.' + caid, value);
          } else {
            instance.attr(property, value);
          }

          instance.save()
            .done(function () {
              $(document.body).trigger('ajax:flash', {
                success: 'Saved'
              });
            })
            .fail(function () {
              this.attr('context.value', this.attr('_value'));
              $(document.body).trigger('ajax:flash', {
                error: 'There was a problem saving'
              });
            }.bind(this))
            .always(function () {
              this.attr('isSaving', false);
            }.bind(this));
        }.bind(this));
      }
    },
    init: function () {
      var scope = this.scope;
      var value = scope.attr('value');
      var values = scope.attr('values');
      var property = scope.attr('property');
      var instance = scope.attr('instance');
      var type = scope.attr('type');
      if (scope.attr('caId')) {
        if (type === 'checkbox') {
          value = value === '1';
        }
        if (type === 'person') {
          if (value && value instanceof can.Map) {
            value = value.serialize();
          }
          value = _.isEmpty(value) ? undefined : value;
        }
        if (type === 'dropdown') {
          if (_.isNull(value) || _.isUndefined(value)) {
            value = '';
          }
        }
      }
      if (property) {
        value = instance.attr(property);
      }
      scope.attr('_value', value);
      scope.attr('context.value', value);

      if (values && _.isString(values)) {
        values = values.split(',');
      }
      scope.attr('context.values', values);
    },
    events: {
      '{window} mousedown': function (el, ev) {
        var isInside = this.element.has(ev.target).length ||
                   this.element.is(ev.target);

        if (!isInside &&
            this.scope.attr('context.isEdit')) {
          _.defer(function () {
            this.scope.onSave(this.scope, this.element, ev);
          }.bind(this));
        }
      }
    }
  });
})(window.can, window.can.$);
