window.onload = function() { 
    const popup = document.getElementById("popup");
    const closePopupButton = document.getElementById("close-popup");
    const generateSummaryButton = document.getElementById("generate-summary");
    
    // Check if the popup has been shown from localStorage
    const isPopupShown = localStorage.getItem("isPopupShown");

    if (!isPopupShown) {
   
        popup.style.display = "flex";
        localStorage.setItem("isPopupShown", "true");
    }

    // The popup will close permanently when the close button is clicked
    closePopupButton.addEventListener("click", function() {
        popup.style.display = "none";
    });

    // When the generate summary button is clicked
    generateSummaryButton.addEventListener("click", function(event) {
        // Disable the button and change its state
        generateSummaryButton.classList.add("disabled-button");
        generateSummaryButton.textContent = "Generating summary..."; 
        generateSummaryButton.style.backgroundColor = "#b3b3b3"; 

    });
};
