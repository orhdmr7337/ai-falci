// Form gönderimlerinde yükleme animasyonu
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.fortune-form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const button = this.querySelector('button[type="submit"]');
            button.disabled = true;
            button.innerHTML = '<span class="loading">Yorumlanıyor...</span>';
        });
    });

    // Dosya yükleme önizlemesi
    const fileInput = document.getElementById('coffee-image');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.createElement('img');
                    preview.src = e.target.result;
                    preview.className = 'image-preview';
                    
                    const container = document.querySelector('.form-group');
                    const existingPreview = container.querySelector('.image-preview');
                    if (existingPreview) {
                        container.removeChild(existingPreview);
                    }
                    container.appendChild(preview);
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Animasyonlu scroll
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

    // Mandala arka plan animasyonu
    const mandala = document.querySelector('.mandala-bg');
    if (mandala) {
        window.addEventListener('scroll', () => {
            const rotation = window.scrollY / 10;
            mandala.style.transform = `rotate(${rotation}deg)`;
        });
    }

    // Form doğrulama
    const validateForm = (form) => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('error');
                
                const errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.textContent = 'Bu alan zorunludur';
                
                const existingError = input.parentNode.querySelector('.error-message');
                if (!existingError) {
                    input.parentNode.appendChild(errorMsg);
                }
            } else {
                input.classList.remove('error');
                const existingError = input.parentNode.querySelector('.error-message');
                if (existingError) {
                    existingError.remove();
                }
            }
        });

        return isValid;
    };

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}); 