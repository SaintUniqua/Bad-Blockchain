// EduChain UI Enhancements
// Sidebar Toggle and Dark Mode Handler

document.addEventListener('DOMContentLoaded', function() {
    // Remove no-transition class so CSS transitions work after initial paint
    requestAnimationFrame(function() {
        requestAnimationFrame(function() {
            document.documentElement.classList.remove('no-transition');
        });
    });
    
    // ============================================
    // DARK MODE FUNCTIONALITY
    // ============================================
    
    // Theme already applied in <head> before paint — just read it here for reference
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    
    // Dark mode toggle button
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Add a subtle animation
            this.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                this.style.transform = 'rotate(0deg)';
            }, 300);
        });
    }
    
    // ============================================
    // SIDEBAR TOGGLE FUNCTIONALITY
    // ============================================
    
    // Check for saved sidebar state or default to 'collapsed'
    const savedSidebarState = localStorage.getItem('sidebarExpanded') === 'true';
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebar && savedSidebarState) {
        sidebar.classList.add('expanded');
    }
    
    // Sidebar toggle button
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarLogo = document.querySelector('.sidebar-logo');
    
    function toggleSidebar() {
        if (sidebar) {
            sidebar.classList.toggle('expanded');
            const isExpanded = sidebar.classList.contains('expanded');
            localStorage.setItem('sidebarExpanded', isExpanded);
        }
    }
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Also toggle on logo click
    if (sidebarLogo) {
        sidebarLogo.addEventListener('click', toggleSidebar);
    }
    
    // ============================================
    // NAVIGATION ACTIVE STATE
    // ============================================
    
    // Highlight active navigation item based on current page
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    const headerNavItems = document.querySelectorAll('.header-nav-link');
    
    // Sidebar navigation active state
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            item.classList.add('active');
        } else if (currentPath.startsWith(href) && href !== '/') {
            item.classList.add('active');
        }
    });
    
    // Header navigation active state
    headerNavItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath) {
            item.classList.add('active');
        } else if (href !== '/' && currentPath.startsWith(href)) {
            item.classList.add('active');
        }
    });
    
    // ============================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ============================================
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ============================================
    // CARD ANIMATIONS ON SCROLL
    // ============================================
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.5s ease-out';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe cards for animation
    document.querySelectorAll('.stat-card, .block-card, .transaction-card').forEach(card => {
        observer.observe(card);
    });
    
    // ============================================
    // FLASH MESSAGE AUTO-DISMISS
    // ============================================
    
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000); // Auto-dismiss after 5 seconds
    });
    
    // ============================================
    // COPY TO CLIPBOARD FUNCTIONALITY
    // ============================================
    
    // Add click-to-copy for code blocks
    document.querySelectorAll('code').forEach(codeBlock => {
        codeBlock.style.cursor = 'pointer';
        codeBlock.title = 'Click to copy';
        
        codeBlock.addEventListener('click', function() {
            const text = this.textContent;
            navigator.clipboard.writeText(text).then(() => {
                // Show feedback
                const originalText = this.textContent;
                this.textContent = 'âœ“ Copied!';
                this.style.color = '#22c55e';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.color = '';
                }, 1500);
            });
        });
    });
    
    // ============================================
    // FORM VALIDATION ENHANCEMENTS
    // ============================================
    
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.style.opacity = '0.6';
                submitButton.style.cursor = 'not-allowed';
                
                // Re-enable after 2 seconds to prevent accidental double-submit
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.style.opacity = '1';
                    submitButton.style.cursor = 'pointer';
                }, 2000);
            }
        });
    });
    
    // ============================================
    // NUMBER INPUT FORMATTING
    // ============================================
    
    // Format balance displays with thousand separators
    document.querySelectorAll('.balance-value, .stat-value').forEach(element => {
        const value = parseFloat(element.textContent.replace(/[^0-9.-]/g, ''));
        if (!isNaN(value)) {
            const formatted = value.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            element.textContent = element.textContent.replace(/[0-9,.]+/, formatted);
        }
    });
    
    // ============================================
    // RESPONSIVE SIDEBAR BEHAVIOR
    // ============================================
    
    // Auto-collapse sidebar on mobile when clicking outside
    if (window.innerWidth <= 768) {
        document.addEventListener('click', function(e) {
            if (sidebar && sidebar.classList.contains('expanded')) {
                if (!sidebar.contains(e.target)) {
                    sidebar.classList.remove('expanded');
                    localStorage.setItem('sidebarExpanded', 'false');
                }
            }
        });
    }
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            // On mobile, always collapse sidebar
            if (window.innerWidth <= 768 && sidebar) {
                sidebar.classList.remove('expanded');
                localStorage.setItem('sidebarExpanded', 'false');
            }
        }, 250);
    });
    
    // ============================================
    // TRANSACTION AMOUNT INPUT VALIDATION
    // ============================================
    
    const amountInput = document.querySelector('input[name="amount"]');
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            // Ensure only positive numbers with 2 decimal places
            let value = this.value;
            
            // Remove non-numeric characters except decimal point
            value = value.replace(/[^0-9.]/g, '');
            
            // Ensure only one decimal point
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            
            // Limit to 2 decimal places
            if (parts.length === 2 && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].substring(0, 2);
            }
            
            this.value = value;
        });
    }
    
    // ============================================
    // LOADING STATES FOR MINING
    // ============================================
    
    const miningForm = document.querySelector('.mining-form');
    if (miningForm) {
        miningForm.addEventListener('submit', function(e) {
            const button = this.querySelector('button[type="submit"]');
            if (button) {
                button.innerHTML = 'â›ï¸ Mining... Please wait';
                button.disabled = true;
                
                // Add a pulsing animation
                button.style.animation = 'pulse 1.5s infinite';
            }
        });
    }
    
    // ============================================
    // TOOLTIP FUNCTIONALITY
    // ============================================
    
    // Add tooltips to truncated addresses
    document.querySelectorAll('code').forEach(code => {
        if (code.textContent.includes('...')) {
            code.style.position = 'relative';
            
            code.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = 'Click to copy';
                tooltip.style.cssText = `
                    position: absolute;
                    bottom: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0, 0, 0, 0.9);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    margin-bottom: 4px;
                    z-index: 1000;
                `;
                this.appendChild(tooltip);
            });
            
            code.addEventListener('mouseleave', function() {
                const tooltip = this.querySelector('.custom-tooltip');
                if (tooltip) {
                    tooltip.remove();
                }
            });
        }
    });
    
    // ============================================
    // CONSOLE WELCOME MESSAGE
    // ============================================
    
    console.log('%câ›“ï¸ EduChain', 'font-size: 24px; font-weight: bold; color: #3b82f6;');
    console.log('%cEducational Blockchain Platform', 'font-size: 14px; color: #64748b;');
    console.log('%cTheme: ' + currentTheme, 'font-size: 12px; color: #94a3b8;');
    
});