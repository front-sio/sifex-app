// Sidebar Menu Enhancement Script
// This ensures sidebar functionality works on all pages, including empty ones

(function($) {
    'use strict';

    // Sidebar menu initialization
    function initSidebarMenu() {
        // Remove any existing handlers to prevent duplicates
        $('#sidebar-menu .submenu > a').off('click.sidebarMenu');
        
        // Add click handlers for submenu items
        $('#sidebar-menu .submenu > a').on('click.sidebarMenu', function(e) {
            var $this = $(this);
            var $parent = $this.parent();
            
            // Check if this is a submenu item
            if ($parent.hasClass('submenu')) {
                e.preventDefault();
                
                // Toggle submenu
                if (!$this.hasClass('subdrop')) {
                    // Close all other submenus in the same level
                    $this.closest('ul').find('.submenu > a.subdrop').removeClass('subdrop').next('ul').slideUp(250);
                    
                    // Open this submenu
                    $this.addClass('subdrop').next('ul').slideDown(350);
                } else {
                    // Close this submenu
                    $this.removeClass('subdrop').next('ul').slideUp(250);
                }
                
                return false;
            }
        });
        
        // Set active menu items based on current URL
        setActiveMenuItem();
    }
    
    // Set active menu item based on current page
    function setActiveMenuItem() {
        var currentPath = window.location.pathname;
        var $activeLink = null;
        
        // Find the best matching menu item
        $('#sidebar-menu a').each(function() {
            var $this = $(this);
            var href = $this.attr('href');
            
            if (href && href !== 'javascript:void(0);' && href !== '#') {
                if (currentPath === href || (href !== '/' && currentPath.indexOf(href) !== -1)) {
                    $activeLink = $this;
                    return false; // Break the loop
                }
            }
        });
        
        // Remove previous active classes
        $('#sidebar-menu a').removeClass('active');
        $('#sidebar-menu .submenu').removeClass('active');
        
        // Set active class and open parent submenu if needed
        if ($activeLink) {
            $activeLink.addClass('active');
            
            var $submenuParent = $activeLink.closest('.submenu');
            if ($submenuParent.length) {
                $submenuParent.addClass('active');
                $submenuParent.children('a').addClass('subdrop');
                $activeLink.closest('ul').show();
            }
        }
    }
    
    // Initialize when document is ready
    $(document).ready(function() {
        // Small delay to ensure all DOM elements are loaded
        setTimeout(initSidebarMenu, 100);
        
        // Re-initialize after page changes (for SPA behavior)
        $(window).on('popstate', function() {
            setTimeout(initSidebarMenu, 100);
        });
        
        // Re-initialize after AJAX content loads
        $(document).ajaxComplete(function() {
            setTimeout(initSidebarMenu, 100);
        });
    });
    
    // Fallback initialization for late-loading content
    $(window).on('load', function() {
        setTimeout(initSidebarMenu, 200);
    });

})(jQuery);
