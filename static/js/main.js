// Rick and Morty App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Theme Switcher Functionality
    const themeSwitcher = document.getElementById('themeSwitcher');
    const htmlElement = document.documentElement;
    
    // Detect system theme preference
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Load saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    let currentTheme;
    
    if (savedTheme) {
        currentTheme = savedTheme;
    } else {
        // First visit - use system preference
        currentTheme = systemPrefersDark ? 'dark' : 'light';
        localStorage.setItem('theme', currentTheme);
    }
    
    const isDarkMode = currentTheme === 'dark';
    
    // Apply saved theme
    if (isDarkMode) {
        htmlElement.setAttribute('data-theme', 'dark');
        themeSwitcher.checked = true;
    } else {
        htmlElement.setAttribute('data-theme', 'light');
        themeSwitcher.checked = false;
    }
    
    // Theme switcher event listener
    themeSwitcher.addEventListener('change', function() {
        const newTheme = this.checked ? 'dark' : 'light';
        
        // Add transition class for smooth animation
        document.body.style.transition = 'all 0.3s ease';
        
        // Apply new theme
        htmlElement.setAttribute('data-theme', newTheme);
        
        // Save preference and mark as user choice
        localStorage.setItem('theme', newTheme);
        localStorage.setItem('theme-user-preference', 'true');
        
        // Show notification
        const themeText = newTheme === 'dark' ? '🌙 Тёмная' : '☀️ Светлая';
        RickAndMortyApp.showNotification(
            `${themeText} тема активирована!`, 
            'success'
        );
        
        // Remove transition after animation
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
        
        console.log(`🎨 Theme switched to: ${newTheme}`);
    });
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        // Only auto-switch if user hasn't manually set a preference
        const userHasPreference = localStorage.getItem('theme-user-preference') === 'true';
        
        if (!userHasPreference) {
            const newTheme = e.matches ? 'dark' : 'light';
            htmlElement.setAttribute('data-theme', newTheme);
            themeSwitcher.checked = newTheme === 'dark';
            localStorage.setItem('theme', newTheme);
            
            RickAndMortyApp.showNotification(
                `🔄 Тема автоматически изменена на ${newTheme === 'dark' ? 'тёмную' : 'светлую'} (системная настройка)`, 
                'info'
            );
            
            console.log(`🎨 System theme changed to: ${newTheme}`);
        }
    });

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add fade-in animation to cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });

    // Enhanced search functionality with loaders
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="q"]');
        const searchType = searchForm.querySelector('select[name="type"]');
        const searchBtn = searchForm.querySelector('button[type="submit"]');
        
        // Auto-submit form on type change with loading
        if (searchType) {
            searchType.addEventListener('change', function() {
                if (searchInput && searchInput.value.trim()) {
                    showSearchLoading();
                    searchForm.submit();
                }
            });
        }

        // Enhanced search with loading states
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                if (searchInput && searchInput.value.trim()) {
                    showSearchLoading();
                }
            });
        }
        
        // Show loading state for search
        function showSearchLoading() {
            if (searchBtn) {
                const originalContent = searchBtn.innerHTML;
                searchBtn.innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
                searchBtn.disabled = true;
                
                // Restore button after timeout (fallback)
                setTimeout(() => {
                    searchBtn.innerHTML = originalContent;
                    searchBtn.disabled = false;
                }, 5000);
            }
            
            // Show search skeletons if on search page
            if (window.location.pathname.includes('search')) {
                const searchResults = document.querySelector('.search-results, #search-results');
                if (searchResults) {
                    RickAndMortyApp.loading.showSearchSkeletons(searchResults, 5);
                }
            }
        }

        // Live search suggestions with debouncing
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    // Here you could add live search suggestions
                    console.log('🔍 Search query:', this.value);
                }, 300);
            });
        }
    }

    // Filter form enhancements (simplified)
    const filterForms = document.querySelectorAll('.filter-form form');
    filterForms.forEach(form => {
        const selectInputs = form.querySelectorAll('select'); // Only select elements for auto-submit
        selectInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Don't interfere with browser behavior, just submit
                form.submit();
            });
        });
    });

    // Character card hover effects
    document.querySelectorAll('.card').forEach(card => {
        // Only add hover effects if card doesn't contain a link
        if (!card.querySelector('a[href*="character"]')) {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        }
    });

    // Lazy loading for images
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });

    // Portal effect for special buttons
    document.querySelectorAll('.portal-effect').forEach(element => {
        element.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Back to top button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
    backToTopBtn.style.display = 'none';
    backToTopBtn.style.zIndex = '1000';
    backToTopBtn.setAttribute('data-bs-toggle', 'tooltip');
    backToTopBtn.setAttribute('data-bs-placement', 'left');
    backToTopBtn.setAttribute('title', 'Наверх');
    
    document.body.appendChild(backToTopBtn);

    // Show/hide back to top button
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    // Back to top functionality
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Initialize tooltip for back to top button
    new bootstrap.Tooltip(backToTopBtn);

    // Enhanced pagination with skeleton loading
    document.querySelectorAll('.pagination a').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't interfere with browser navigation
            if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) {
                return; // Let browser handle
            }
            
            // Add loading spinner to clicked page link
            const originalText = this.innerHTML;
            this.innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
            this.style.pointerEvents = 'none';
            
            // Show skeletons in content area
            const contentArea = document.querySelector('.row[class*="col-"]')?.parentElement;
            if (contentArea) {
                const pageType = window.location.pathname.includes('character') ? 'character' : 
                               window.location.pathname.includes('episode') ? 'episode' : 
                               window.location.pathname.includes('location') ? 'location' : 'character';
                
                // Small delay to show loading state
                setTimeout(() => {
                    RickAndMortyApp.loading.showSkeletons(contentArea, pageType, 6);
                }, 50);
            }
            
            // Restore original state if navigation fails
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.pointerEvents = 'auto';
            }, 5000);
        });
    });

    // Enhanced search with keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
    });

    // Add status indicators for API calls
    function showApiStatus(status) {
        const statusIndicator = document.createElement('div');
        statusIndicator.className = `alert alert-${status === 'loading' ? 'info' : status === 'success' ? 'success' : 'warning'} position-fixed top-0 end-0 m-3`;
        statusIndicator.style.zIndex = '1060';
        
        if (status === 'loading') {
            statusIndicator.innerHTML = '<i class="bi bi-hourglass-split"></i> Загрузка данных...';
        } else if (status === 'success') {
            statusIndicator.innerHTML = '<i class="bi bi-check-circle"></i> Данные загружены';
        } else {
            statusIndicator.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Данные из кэша';
        }
        
        document.body.appendChild(statusIndicator);
        
        setTimeout(() => {
            statusIndicator.remove();
        }, 3000);
    }

    // Monitor for API calls (you can integrate this with your actual API calls)
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        showApiStatus('loading');
        return originalFetch.apply(this, args)
            .then(response => {
                showApiStatus('success');
                return response;
            })
            .catch(error => {
                showApiStatus('error');
                throw error;
            });
    };

    // Demo function to show skeletons (for testing)
    window.demoSkeletons = function() {
        const container = document.querySelector('#characters-grid, #search-results');
        if (container) {
            const pageType = window.location.pathname.includes('character') ? 'character' : 
                           window.location.pathname.includes('episode') ? 'episode' : 
                           window.location.pathname.includes('search') ? 'character' : 'character';
            
            RickAndMortyApp.loading.showSkeletons(container, pageType, 6);
            
            // Auto-hide after 3 seconds
            setTimeout(() => {
                location.reload();
            }, 3000);
        }
    };
    
    // Add loading to detail page links only (not list pages)
    document.querySelectorAll('a[href*="character-detail"], a[href*="episode-detail"], a[href*="location-detail"]').forEach(link => {
        if (!link.href.includes('#') && !link.classList.contains('page-link')) {
            link.addEventListener('click', function(e) {
                // Don't interfere with browser navigation
                if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.which === 2) {
                    return; // Let browser handle
                }
                
                const targetContainer = document.querySelector('.main-content');
                if (targetContainer) {
                    RickAndMortyApp.loading.showOverlay(targetContainer, 'Загрузка страницы...');
                }
            });
        }
    });

    console.log('🚀 Rick and Morty App initialized with skeleton loaders!');
});

// Utility functions
const RickAndMortyApp = {
    // Loading and Skeleton management
    loading: {
        // Show skeleton loaders
        showSkeletons: function(container, type = 'character', count = 6) {
            const skeletonTemplate = document.querySelector(`#skeleton-templates .${type}-skeleton`);
            if (!skeletonTemplate || !container) return;
            
            container.innerHTML = '';
            
            for (let i = 0; i < count; i++) {
                const skeleton = skeletonTemplate.cloneNode(true);
                skeleton.style.display = 'block';
                
                if (type === 'character') {
                    container.appendChild(this.wrapInColumn(skeleton));
                } else {
                    container.appendChild(skeleton);
                }
            }
            
            console.log(`🦴 Showing ${count} ${type} skeletons`);
        },
        
        // Show search result skeletons
        showSearchSkeletons: function(container, count = 5) {
            const skeletonTemplate = document.querySelector('#skeleton-templates .search-result-skeleton');
            if (!skeletonTemplate || !container) return;
            
            container.innerHTML = '';
            
            for (let i = 0; i < count; i++) {
                const skeleton = skeletonTemplate.cloneNode(true);
                skeleton.style.display = 'block';
                container.appendChild(skeleton);
            }
            
            console.log(`🔍 Showing ${count} search result skeletons`);
        },
        
        // Wrap skeleton in Bootstrap column for grid layout
        wrapInColumn: function(element) {
            const col = document.createElement('div');
            col.className = 'col-lg-4 col-md-6 mb-4';
            col.appendChild(element);
            return col;
        },
        
        // Show spinner loader
        showSpinner: function(container, type = 'portal', message = 'Загрузка...') {
            if (!container) return;
            
            const spinnerClass = type === 'rick' ? 'spinner-rick' : 'spinner-portal';
            container.innerHTML = `
                <div class="text-center py-5">
                    <div class="${spinnerClass}"></div>
                    <div class="loading-text">${message}</div>
                </div>
            `;
            
            console.log(`⚡ Showing ${type} spinner: ${message}`);
        },
        
        // Show loading overlay on element
        showOverlay: function(element, message = 'Загрузка...') {
            if (!element) return;
            
            // Remove existing overlay
            this.hideOverlay(element);
            
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div>
                    <div class="spinner-portal"></div>
                    <div class="loading-text">${message}</div>
                </div>
            `;
            
            element.style.position = 'relative';
            element.appendChild(overlay);
            
            console.log(`📱 Showing overlay: ${message}`);
        },
        
        // Hide loading overlay
        hideOverlay: function(element) {
            if (!element) return;
            
            const overlay = element.querySelector('.loading-overlay');
            if (overlay) {
                overlay.remove();
                console.log('📱 Hiding overlay');
            }
        },
        
        // Hide all loading states
        hide: function(container) {
            if (!container) return;
            
            // Remove skeletons and spinners
            const skeletons = container.querySelectorAll('.skeleton-card, .search-result-skeleton, .spinner-portal, .spinner-rick');
            skeletons.forEach(skeleton => skeleton.remove());
            
            // Remove loading text
            const loadingTexts = container.querySelectorAll('.loading-text');
            loadingTexts.forEach(text => text.remove());
            
            console.log('🧹 Hiding all loading states');
        }
    },

    // Theme management
    theme: {
        get: function() {
            return localStorage.getItem('theme') || 'light';
        },
        
        set: function(theme) {
            if (theme !== 'light' && theme !== 'dark') {
                console.warn('Invalid theme:', theme);
                return;
            }
            
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            
            const themeSwitcher = document.getElementById('themeSwitcher');
            if (themeSwitcher) {
                themeSwitcher.checked = theme === 'dark';
            }
            
            console.log(`🎨 Theme set to: ${theme}`);
        },
        
        toggle: function() {
            const currentTheme = this.get();
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            this.set(newTheme);
            return newTheme;
        },
        
        isDark: function() {
            return this.get() === 'dark';
        }
    },

    // Format character status
    formatStatus: function(status) {
        const statusMap = {
            'alive': { text: 'Живой', class: 'status-alive' },
            'dead': { text: 'Мертвый', class: 'status-dead' },
            'unknown': { text: 'Неизвестно', class: 'status-unknown' }
        };
        return statusMap[status] || { text: status, class: 'status-unknown' };
    },

    // Format gender
    formatGender: function(gender) {
        const genderMap = {
            'male': { text: 'Мужской', class: 'gender-male' },
            'female': { text: 'Женский', class: 'gender-female' },
            'genderless': { text: 'Бесполый', class: 'gender-genderless' },
            'unknown': { text: 'Неизвестно', class: 'gender-unknown' }
        };
        return genderMap[gender] || { text: gender, class: 'gender-unknown' };
    },

    // Create loading placeholder
    createLoadingPlaceholder: function() {
        return `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3 text-muted">Загружаем данные из мультивселенной...</p>
            </div>
        `;
    },

    // Show notification
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '1060';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
};

// Make utility functions globally available
window.RickAndMortyApp = RickAndMortyApp;
