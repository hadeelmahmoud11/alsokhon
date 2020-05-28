$(document).ready(function(){
    $('.ks-loader-outer').fadeOut();
//     Changed title of wishlist at detail page
     $('.o_add_wishlist_dyn').attr('title','Add To Wishlist');
    $('[data-toggle="tooltip"]').tooltip();


      function mobileToggleView(){
            $('.search_container:not(.search-container-7) .mobile-toggle-button #search-btn').click(function(ev){
                $(".search-query").val("");
                if($('.search_container:not(.search-container-7)').hasClass('search__in')){
                    $('.search_container:not(.search-container-7)').removeClass('search__in');
                } else {
                    $('.search_container:not(.search-container-7)').addClass('search__in');
                }

                if($(this).hasClass('fa-search')) {
                    $(this).removeClass('fa-search');
                    $(this).addClass('fa-times');
                }
                else {
                    $(this).removeClass('fa-times');
                    $(this).addClass('fa-search');
                }
          });
       }
       mobileToggleView();


         if($(document).width() < 767) {
            // This is used to remove class for product detail page  vertical multi image responsiveness fix
             if($('#ks_verti_img').hasClass('ks_test_vertical')){
                  $('#ks_verti_img').removeClass('ks_test_vertical');
             }
         };



        if ($('.o_wsale_layout_list').length){
            $('.o_wsale_layout_list').find('.o_wsale_products_grid_table_wrapper').addClass('ks_products_table ks-product-list-view m-auto');
        }
        else{
          $('#products_grid').addClass('ks_products_table');
        }
        $(document).on('hide.bs.modal',$('.o_select_options').parents('.modal').attr('id'), function(ev){
               $('#product_details').removeClass('ks_cart_on_product_detail');
                });
        if(parseInt($('.page_count').val())===1){
                 $('.product_load_more').addClass('d-none');
        }


        $(".ks-scroll-top").click(function() {
          $("html, body").animate({ scrollTop: 0 },1200);
        });
        //     Class for payment page
        $('.ks_shop_payment').parents('.row').addClass('ks_payment_page')


        //open filter
        //Hide default pagination if products getting load using ajax
        $('.ks_filter_button').click(function(){
            $('#products_grid_before').addClass('ks-show-filter');
             if($(".is_ks_load_ajax").length > 0){
                $('.ks-price-filter-apply').addClass('d-none')
             }
             else{
                $('.ks-price-filter-apply').removeClass('d-none')
               _.each($(".products_pager .pagination"),function(pager){
                    $(pager).removeClass("d-none");
                });
             }
             $('#products_grid_before').removeClass('ks-hide-filter');
            $('.ks-filter-overlay').addClass('d-block');
            $('body').addClass('js-no-scroll');
        });

        //close filter  '.filter-heading-panel'
         $('.ks-filter-overlay').on('click', function(e) {
            $('#products_grid_before').addClass('ks-hide-filter');
            $('.ks-filter-overlay').delay(500).queue(function() {
                $('#products_grid_before').removeClass('ks-show-filter');
                 $('.ks-filter-overlay').removeClass('d-block');
                 $('body').removeClass('js-no-scroll');
                 $('.ks-filter-overlay').dequeue();
             });

        });

    //search for header 6
	$('.ks-search-trigger').click(function(){
	    $('.ks-header-6-search').toggleClass('js-search-show');
	    $(this).toggleClass('js-search-hide');
	});

    $('.js_usermenu').parent().addClass('ks_landing_menu');

    if($('.ks-filter-outer .nav-link input[type="checkbox"]').prop("checked") == true) {
        $('.ks-filter-outer .nav-link input[checked="checked"]').parents("ul.collapse").prev().trigger( "click" ); ;
    }



        //correcting z-index on header 7's input click
         $('.search-container-7 input').focusin(function() {
                $('#wrapwrap').addClass('js-change-indexes-h7');
         });

        $('.search-container-7 input').focusout(function() {
                $('#wrapwrap').removeClass('js-change-indexes-h7');
         });
         if ($('.o_wsale_my_cart').find('sup').text()==''){
         $('.o_wsale_my_cart').find('sup').text('0');
         $('.o_wsale_my_cart').removeClass('d-none');
         }
         //correcting z-index on header 8's input click
         $('.ks-header-8-topmost .nav__search_icon').click(function() {
                $('#wrapwrap').toggleClass('js-change-indexes-h8');
         });
        //Handling category mega menu after scrolling
        $(document).on('mouseenter','.ks_vertical_tabs .nav-tabs .nav-link',function(){
            $(this).trigger('click');
            var a = this.href.split("#")[1]
            $('.ks_cat_menu').removeClass('active')
            $('.'+a).addClass('active')
        });
        // Handling multiple multitab active
        $(document).on('click','#new_arrivals',function(ev){
            var a=ev.currentTarget.parentElement.href.split('#')[1]
            var slider_id=$('.'+a+'slider_id').val()
            $('.ks_multitab-'+slider_id).removeClass('active')
            $('.'+a).addClass('active ')
            $('.ks_tab_list'+slider_id).find('a').removeClass('active')
            $('.'+a+'slider_id').siblings().addClass('active');
        })

    // ***** triggering animation when in Screen viewport ***** \\
        $('.animated').addClass('no-animation');
         function inViewport(){
             $('.no-animation').each(function(){
                 var divPos = $(this).offset().top,
                     topOfWindow = $(window).scrollTop();

                 if( divPos < topOfWindow + 600 ){
                     $(this).removeClass('no-animation');
                 }
             });
         }

         $(window).scroll(function(){
             inViewport();
         });
         $(window).on("resize", function (e) {
            inViewport();
             if($(window).width() < 1280){
                $('body').removeClass('toggle-navigation');
                $('body > #wrapwrap').removeClass('js-menu-opened');
                $('body').removeClass('js-menu-opened');
                $('.navbar-collapse').removeClass('show');
             }
         });


         //for stopping extra menus click
        $(document).on("show.bs.dropdown","li.o_extra_menu_items",function(ev){
             return false;
         });

         function mobileToggle(){
            $(document).on('click','.o_affix_enabled button.navbar-toggler',function(){
               if ($('body > #wrapwrap').hasClass('js-menu-opened')) {
                   $('body > #wrapwrap').removeClass('js-menu-opened');
                   $('body').removeClass('toggle-navigation');
               }
               else{
                    $('body > #wrapwrap').addClass('js-menu-opened');
                    $('body').addClass('toggle-navigation');
                }
            });
            $(document).on('click','.o_header_affix .navbar-toggler',function(){
              $('body').toggleClass('js-menu-opened');
           });
         }
        //for stopping scroll while navbar menu is opened
        mobileToggle();

        var filter_len = $('.ks-filter-outer').length;
        if(!filter_len){
            $('#products_grid_before').addClass("ks-only-categories");
            $('.dropdown_ppg').addClass('d-none');
        }

       var is_custom_sign_up = $(".ks-custom-login").length;
       if(is_custom_sign_up){
           $('.ks-default-login').addClass('d-none')
        }

        if($(window).width() < 990){
          $('.navbar-expand-md').addClass('navbar-expand-lg ks-default-header');
          $('.ks-default-header').removeClass('navbar-expand-md');

         }

         _.each($('.ks_menu_heading'),function(ev){
            if ($(ev).text()==' '){
            $(ev).removeClass('d-block')
            $(ev).addClass('d-none')
            }
         })

         $(document).on('click','.navbar-toggler',function(ev){
            $('.ks-header-offer').toggleClass('ks_header_menu_toggled');
         });

         //Footer fix for shop page only
         $('#product_detail').parents("main").next().addClass("ks_shop_page_footer");

         new WOW().init();
         if ($('.ks-header-11').length){
            if ($('.mainTransparent').length){
             $(document).find('body').addClass('ks_transparent_header')
        }}


            var initScrollTop = $(window).scrollTop();
            $('.parallax-3 img').css('transform','translateY('+(initScrollTop)+'px)');
            $('.parallax-2 img').css('transform','translateY('+(initScrollTop)+'px)');
            $('.ks-ny-hero-text').css('transform','translateY('+(initScrollTop)+'px)');

        $(window).scroll(function() {
            var scrollTop = $(window).scrollTop();
            $('.parallax-3 img').css('transform','translateY('+(scrollTop*0.5)+'px)');
            $('.parallax-2 img').css('transform','translateY('+(scrollTop/3)+'px)');
            $('.ks-ny-hero-text').css('transform','translateY('+(scrollTop*0.5)+'px)');
         });

        (function() {
            var requestAnimationFrame = window.requestAnimationFrame || window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame || window.msRequestAnimationFrame ||
            function(callback) {
                window.setTimeout(callback, 1000 / 60);
            };
            window.requestAnimationFrame = requestAnimationFrame;
        })();

        var flakes = [],
         canvas = $("#snow-fall")
         if (canvas.length){
            canvas =$("#snow-fall")[0],
            ctx = canvas.getContext("2d"),
            flakeCount = 400,
            mX = -100,
            mY = -100

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            function snow() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                for (var i = 0; i < flakeCount; i++) {
                    var flake = flakes[i],
                        x = mX,
                        y = mY,
                        minDist = 150,
                        x2 = flake.x,
                        y2 = flake.y;

                    var dist = Math.sqrt((x2 - x) * (x2 - x) + (y2 - y) * (y2 - y)),
                        dx = x2 - x,
                        dy = y2 - y;

                    if (dist < minDist) {
                        var force = minDist / (dist * dist),
                            xcomp = (x - x2) / dist,
                            ycomp = (y - y2) / dist,
                            deltaV = force / 2;

                        flake.velX -= deltaV * xcomp;
                        flake.velY -= deltaV * ycomp;

                    } else {
                        flake.velX *= .98;
                        if (flake.velY <= flake.speed) {
                            flake.velY = flake.speed
                        }
                        flake.velX += Math.cos(flake.step += .05) * flake.stepSize;
                    }

                    ctx.fillStyle = "rgba(255,255,255," + flake.opacity + ")";
                    flake.y += flake.velY;
                    flake.x += flake.velX;

                    if (flake.y >= canvas.height || flake.y <= 0) {
                        reset(flake);
                    }


                    if (flake.x >= canvas.width || flake.x <= 0) {
                        reset(flake);
                    }

                    ctx.beginPath();
                    ctx.arc(flake.x, flake.y, flake.size, 0, Math.PI * 2);
                    ctx.fill();
                }
                requestAnimationFrame(snow);
            };

            function reset(flake) {
                flake.x = Math.floor(Math.random() * canvas.width);
                flake.y = 0;
                flake.size = (Math.random() * 3) + 2;
                flake.speed = (Math.random() * 1) + 0.5;
                flake.velY = flake.speed;
                flake.velX = 0;
                flake.opacity = (Math.random() * 0.5) + 0.3;
            }

            function init() {
                for (var i = 0; i < flakeCount; i++) {
                    var x = Math.floor(Math.random() * canvas.width),
                        y = Math.floor(Math.random() * canvas.height),
                        size = (Math.random() * 3) + 2,
                        speed = (Math.random() * 1) + 0.5,
                        opacity = (Math.random() * 0.5) + 0.3;

                    flakes.push({
                        speed: speed,
                        velY: speed,
                        velX: 0,
                        x: x,
                        y: y,
                        size: size,
                        stepSize: (Math.random()) / 30,
                        step: 0,
                        opacity: opacity
                    });
                }

                snow();
            };

            canvas.addEventListener("mousemove", function(e) {
                mX = e.clientX,
                mY = e.clientY
            });

            window.addEventListener("resize",function(){
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            })

            init();
    }
});