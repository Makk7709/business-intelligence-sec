/**
 * Script pour corriger les problèmes d'affichage des graphiques
 * 
 * Ce script doit être inclus après Chart.js et avant l'initialisation des graphiques.
 */

// Fonction pour vérifier si un élément existe dans le DOM
function elementExists(id) {
    return document.getElementById(id) !== null;
}

// Fonction pour vérifier si Chart.js est chargé
function isChartJsLoaded() {
    return typeof Chart !== 'undefined';
}

// Fonction pour corriger les problèmes d'affichage des graphiques
function fixCharts() {
    console.log("Correction des graphiques...");
    
    // Vérifier si Chart.js est chargé
    if (!isChartJsLoaded()) {
        console.error("Chart.js n'est pas chargé. Chargement de Chart.js...");
        
        // Charger Chart.js
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = function() {
            console.log("Chart.js chargé avec succès.");
            initializeCharts();
        };
        document.head.appendChild(script);
        return;
    }
    
    // Initialiser les graphiques
    initializeCharts();
}

// Fonction pour initialiser les graphiques
function initializeCharts() {
    console.log("Initialisation des graphiques...");
    
    // Vérifier si les éléments existent
    if (!elementExists('stockChart')) {
        console.error("L'élément stockChart n'existe pas.");
        return;
    }
    
    // Vérifier si les graphiques comparatifs existent
    const comparativeCharts = [
        'revenueComparisonChart',
        'marginComparisonChart',
        'incomeComparisonChart',
        'growthComparisonChart'
    ];
    
    let allComparativeChartsExist = true;
    for (const chartId of comparativeCharts) {
        if (!elementExists(chartId)) {
            console.error(`L'élément ${chartId} n'existe pas.`);
            allComparativeChartsExist = false;
        }
    }
    
    // Vérifier si les graphiques de prédiction existent
    const predictionCharts = [
        'revenuePredictionChart',
        'marginPredictionChart'
    ];
    
    let allPredictionChartsExist = true;
    for (const chartId of predictionCharts) {
        if (!elementExists(chartId)) {
            console.error(`L'élément ${chartId} n'existe pas.`);
            allPredictionChartsExist = false;
        }
    }
    
    // Charger les données comparatives si tous les graphiques comparatifs existent
    if (allComparativeChartsExist) {
        console.log("Chargement des données comparatives...");
        loadComparativeData();
    }
    
    // Charger les données de prédiction si tous les graphiques de prédiction existent
    if (allPredictionChartsExist) {
        console.log("Chargement des données de prédiction...");
        loadPredictionData();
    }
}

// Exécuter la fonction de correction au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, correction des graphiques...");
    
    // Attendre 1 seconde pour s'assurer que tous les éléments sont chargés
    setTimeout(fixCharts, 1000);
}); 