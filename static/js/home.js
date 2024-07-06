document.getElementById("logo-cuenta").addEventListener("click", function () {
    const casita = document.querySelector("casita");
    casita.style.left = "-100px"; // Mueve el cuadrado 100px hacia la derecha
});

const imageContainer = document.getElementById('image-container');

// get the list of images in the static/img/productos directory
fetch('/static/img/productos')
    .then(response => response.json())
    .then(data => {
        // loop through the list of images and create img elements
        data.forEach(image => {
            const img = document.createElement('img');
            img.src = `/static/img/productos/${image}`;
            img.alt = image;
            imageContainer.appendChild(img);
        });
    })
    .catch(error => console.error('Error loading images:', error));
