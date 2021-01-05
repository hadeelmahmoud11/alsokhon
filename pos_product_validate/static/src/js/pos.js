odoo.define('pos_product_validate.pos', function(require){
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var PopupWidget = require('point_of_sale.popups');
    var QWeb = core.qweb;
    var _t = core._t;
    var rpc = require('web.rpc');

    var utils = require('web.utils');

    var round_pr = utils.round_precision;



    models.load_fields('product.product',['qty_available']);
    var exports = {};


    screens.PaymentScreenWidget.include({

      finalize_validation: function() {
          var self = this;
          var order = this.pos.get_order();

          if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {

                  this.pos.proxy.printer.open_cashbox();
          }

          order.initialize_validation_date();
          var partner_id = order.get_client();
          if (!partner_id){
    				self.gui.show_popup('error',{
    					'title': _t('Unknown customer'),
    					'body': _t('You cannot get the order. Select customer first.'),
    				});
    				return;
    			}
          order.finalized = true;
          if (order.is_to_invoice()) {
              var invoiced = this.pos.push_and_invoice_order(order);
              this.invoicing = true;

              invoiced.catch(this._handleFailedPushForInvoice.bind(this, order, false));

              invoiced.then(function (server_ids) {
                  self.invoicing = false;
                  var post_push_promise = [];
                  post_push_promise = self.post_push_order_resolve(order, server_ids);
                  post_push_promise.then(function () {
                          self.gui.show_screen('receipt');
                  }).catch(function (error) {
                      self.gui.show_screen('receipt');
                      if (error) {
                          self.gui.show_popup('error',{
                              'title': "Error: no internet connection",
                              'body':  error,
                          });
                      }
                  });
              });
          } else {
              var ordered = this.pos.push_order(order);
              if (order.wait_for_push_order()){
                  var server_ids = [];
                  ordered.then(function (ids) {
                    server_ids = ids;
                  }).finally(function() {
                      var post_push_promise = [];
                      post_push_promise = self.post_push_order_resolve(order, server_ids);
                      post_push_promise.then(function () {
                              self.gui.show_screen('receipt');
                          }).catch(function (error) {
                            self.gui.show_screen('receipt');
                            if (error) {
                                self.gui.show_popup('error',{
                                    'title': "Error: no internet connection",
                                    'body':  error,
                                });
                            }
                          });
                    });
              }
              else {
                self.gui.show_screen('receipt');
              }

          }

          self.get_pos_lots();
      },

      get_lots_fields: function () {
        var fields = [];
        return fields;
      },
      get_lots_domain: function(){
        var self = this;
        var from = moment(new Date()).subtract(self.pos.config.lot_expire_days,'d').format('YYYY-MM-DD')+" 00:00:00";
        if(self.pos.config.allow_pos_lot){
            return ['&',['create_date','>=',from],['total_qty','>',0]];
        }
        else{
            return [['id','=',0]];
        }
      },
      get_pos_lots: function () {
        var self = this;
        var product_lot = [];
        var fields = self.get_lots_fields();
        var lot_domain = self.get_lots_domain();
        rpc.query({
            model: 'stock.production.lot',
            method: 'search_read',
            args: [lot_domain,fields],
        }, {async: true}).then(function(output) {
          output.forEach(function(lot) {
              product_lot.push(lot);
              self.pos.set({'list_lot_num' : product_lot});
          });
        });
      },
  	});

    screens.ProductScreenWidget.include({
  		show: function() {
  			var self = this;
  			this._super();
        self.get_pos_products();
  		},
      get_products_fields: function () {
        var fields = ['id','qty_available'];
        return fields;
      },
      get_products_domain: function(){
        var self = this;
        var domain = ['&', '&', ['sale_ok','=',true],['available_in_pos','=',true],'|',['company_id','=',self.pos.config.company_id[0]],['company_id','=',false]];
        if (self.pos.config.limit_categories &&  self.pos.config.iface_available_categ_ids.length) {
            domain.unshift('&');
            domain.push(['pos_categ_id', 'in', self.pos.config.iface_available_categ_ids]);
        }
        if (self.pos.config.iface_tipproduct){
          domain.unshift(['id', '=', self.pos.config.tip_product_id[0]]);
          domain.unshift('|');
        }
        return domain;
      },
      get_pos_products: function () {
        var self = this;
        var fields = self.get_products_fields();
        var pro_domain = self.get_products_domain();
        rpc.query({
            model: 'product.product',
            method: 'search_read',
            args: [pro_domain,fields],
        }, {async: true}).then(function(output) {
          var all = $('.product');
          $.each(all, function(index, value) {
            var product_id = $(value).data('product-id');
            for (var i = 0; i < output.length; i++) {
              if(product_id == output[i].id ){
                var product_qty = output[i].qty_available;
                $(value).find('#availqty').html(product_qty);
                break;
              }
            }
          });
        });
      },
  	});


    return exports;



});
