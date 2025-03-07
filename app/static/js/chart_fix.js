/**
 * Script pour corriger les problèmes d'affichage des graphiques
 * Ce script est chargé après Chart.js et s'assure que les graphiques sont correctement initialisés
 */

// Vérifier si Chart.js est chargé
function isChartJsLoaded() {
    return typeof Chart !== 'undefined';
}

// Vérifier si un élément existe dans le DOM
function elementExists(id) {
    return document.getElementById(id) !== null;
}

// Fonction principale pour corriger les graphiques
function fixCharts() {
    console.log("Exécution de fixCharts()...");
    
    // Vérifier si Chart.js est chargé
    if (!isChartJsLoaded()) {
        console.error("Chart.js n'est pas chargé. Impossible de corriger les graphiques.");
        return;
    }
    
    console.log("Chart.js est chargé. Version : " + Chart.version);
    
    // Liste des IDs de canvas pour les graphiques
    const chartIds = [
        'stockChart',
        'revenueComparisonChart',
        'marginComparisonChart',
        'incomeComparisonChart',
        'growthComparisonChart',
        'revenuePredictionChart',
        'marginPredictionChart'
    ];
    
    // Vérifier si les éléments canvas existent
    for (const id of chartIds) {
        if (elementExists(id)) {
            console.log(`L'élément ${id} existe.`);
        } else {
            console.log(`L'élément ${id} n'existe pas.`);
        }
    }
    
    // Forcer l'appel des fonctions de chargement des données
    if (typeof loadComparativeData === 'function') {
        console.log("Appel de loadComparativeData()...");
        loadComparativeData();
    } else {
        console.log("La fonction loadComparativeData n'existe pas.");
    }
    
    if (typeof loadPredictionData === 'function') {
        console.log("Appel de loadPredictionData()...");
        loadPredictionData();
    } else {
        console.log("La fonction loadPredictionData n'existe pas.");
    }
    
    // Mettre à jour tous les graphiques existants
    Object.keys(Chart.instances).forEach(key => {
        console.log(`Mise à jour du graphique ${key}...`);
        Chart.instances[key].update();
    });
}

// Fonction pour initialiser les graphiques après un délai
function initializeChartsWithDelay() {
    console.log("Initialisation des graphiques avec délai...");
    setTimeout(fixCharts, 500);
}

// Exécuter la correction après le chargement complet de la page
window.addEventListener('load', function() {
    console.log("Page chargée, initialisation des graphiques...");
    initializeChartsWithDelay();
});

// Exécuter également lors de l'événement DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, planification de l'initialisation des graphiques...");
    // Attendre que Chart.js soit chargé
    if (isChartJsLoaded()) {
        initializeChartsWithDelay();
    } else {
        console.log("Chart.js n'est pas encore chargé, attente...");
        // Vérifier toutes les 100ms si Chart.js est chargé
        const checkInterval = setInterval(function() {
            if (isChartJsLoaded()) {
                console.log("Chart.js est maintenant chargé.");
                clearInterval(checkInterval);
                initializeChartsWithDelay();
            }
        }, 100);
        
        // Arrêter la vérification après 5 secondes
        setTimeout(function() {
            clearInterval(checkInterval);
            console.log("Délai d'attente dépassé pour le chargement de Chart.js.");
        }, 5000);
    }
}); 