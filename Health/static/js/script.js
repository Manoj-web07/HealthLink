var swiper = new Swiper('.swiper-container', {
            slidesPerView: 6,  // Show 6 items per slide
            spaceBetween: 10,   // Space between slides
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                1200: {
                    slidesPerView: 6,  // 6 items per slide on large screens
                },
                992: {
                    slidesPerView: 4,  // 4 items per slide on medium screens
                },
                768: {
                    slidesPerView: 3,  // 3 items per slide on tablets
                },
                480: {
                    slidesPerView: 1,  // 1 item per slide on mobile screens
                }
            }
        });var swiper = new Swiper('.swiper-container', {
            slidesPerView: 6,  // Show 6 items per slide
            spaceBetween: 10,   // Space between slides
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                1200: {
                    slidesPerView: 6,  // 6 items per slide on large screens
                },
                992: {
                    slidesPerView: 4,  // 4 items per slide on medium screens
                },
                768: {
                    slidesPerView: 3,  // 3 items per slide on tablets
                },
                480: {
                    slidesPerView: 1,  // 1 item per slide on mobile screens
                }
            }
        });var swiper = new Swiper('.swiper-container', {
            slidesPerView: 6,  // Show 6 items per slide
            spaceBetween: 10,   // Space between slides
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                1200: {
                    slidesPerView: 6,  // 6 items per slide on large screens
                },
                992: {
                    slidesPerView: 4,  // 4 items per slide on medium screens
                },
                768: {
                    slidesPerView: 3,  // 3 items per slide on tablets
                },
                480: {
                    slidesPerView: 1,  // 1 item per slide on mobile screens
                }
            }
        });var swiper = new Swiper('.swiper-container', {
            slidesPerView: 6,  // Show 6 items per slide
            spaceBetween: 10,   // Space between slides
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            breakpoints: {
                1200: {
                    slidesPerView: 6,  // 6 items per slide on large screens
                },
                992: {
                    slidesPerView: 4,  // 4 items per slide on medium screens
                },
                768: {
                    slidesPerView: 3,  // 3 items per slide on tablets
                },
                480: {
                    slidesPerView: 1,  // 1 item per slide on mobile screens
                }
            }
        });

<script>
    function toggleNearby(select) {
        if (select.value === 'nearby') {
            // Optionally, show some additional UI for location fetching, like a loading spinner
            autoFillNearby();  // Call your function to fill location automatically
        }
    }

    function autoFillNearby() {
        // This function should get the user's current location using Geolocation API or similar method
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                // Set the latitude and longitude fields with user's coordinates
                document.getElementById('latitude').value = position.coords.latitude;
                document.getElementById('longitude').value = position.coords.longitude;
                // Optionally, submit the form or trigger additional actions
                document.querySelector('form').submit();
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }
</script>

<script>
    // Show modal when clicking on "Book Appointment" button
    document.getElementById('bookAppointmentBtn').addEventListener('click', function() {
        var myModal = new bootstrap.Modal(document.getElementById('appointmentRequestModal'));
        myModal.show();
    });

    // Handle form submission using AJAX
    document.getElementById('appointmentRequestForm').addEventListener('submit', function(event) {
        event.preventDefault();

        var formData = new FormData(this);
        var appointmentDate = document.getElementById('appointmentDate').value;
        formData.append('appointment_date', appointmentDate);

        fetch('{% url "appointment_request" %}', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Appointment request submitted successfully!');
                // Close the modal
                var myModal = bootstrap.Modal.getInstance(document.getElementById('appointmentRequestModal'));
                myModal.hide();
            } else {
                alert('Error submitting appointment request. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
</script>
