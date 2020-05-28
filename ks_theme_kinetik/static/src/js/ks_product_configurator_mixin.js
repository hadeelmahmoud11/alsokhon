odoo.define('ks_theme_kinetik.ProductConfiguratorMixin', function (require) {
    'use strict';

    var ProductConfiguratorMixin = require('sale.VariantMixin');;
    var sAnimations = require('website.content.snippets.animation');
    sAnimations.registry.WebsiteSale.include({
        /**
         * Adds the stock checking to the regular _onChangeCombination method
         * @override
         */
        _onChangeCombination: function (){
            var ks_avail = arguments[1];
            arguments[1] = arguments[1].parent();
            this._super.apply(this, arguments);
            arguments[1] = ks_avail;
            ProductConfiguratorMixin._onChangeCombinationStock.apply(this, arguments);
            var seconds = arguments[2].seconds;
            if(seconds){
             $('.ks_timer_box').removeClass("d-none");
             $('.clock').removeClass("d-none");
             $('.ks_product_timer_title').removeClass("d-none");
             var clock = $('.clock').FlipClock(seconds, {
                clockFace: 'DailyCounter',
                            countdown: true,
                });
            }
            else{
                $('.clock').addClass("d-none");
                $('.ks_timer_box').addClass('d-none');
                $('.ks_product_timer_title').addClass("d-none");
            }

        },
    });

    return ProductConfiguratorMixin;
});