// Gestion du panier et des favoris
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let favorites = JSON.parse(localStorage.getItem('favorites')) || [];

// Fonction pour ajouter au panier avec animation
function addToCart(event) {
    try {
        const button = event.target.closest('.addToCart');
        if (!button) return;
        
        const card = button.closest('.card');
        if (!card) throw new Error('Card not found');

        const name = card.querySelector('.cardName')?.textContent;
        const priceText = card.querySelector('.price')?.textContent;
        const image = card.querySelector('.cardImg img')?.src;

        if (!name || !priceText || !image) {
            throw new Error('Invalid game data');
        }

        // Animation du bouton
        button.classList.add('adding');
        button.disabled = true;

        // Convertir le prix en nombre
        const price = parseFloat(priceText.replace('€', ''));

        const existingGame = cart.find(item => item.name === name);
        if (existingGame) {
            existingGame.quantity++;
        } else {
            cart.push({
                name,
                price,
                image,
                quantity: 1
            });
        }

        localStorage.setItem('cart', JSON.stringify(cart));
        updateCart();
        updateHeaderCounters(); // Mettre à jour les compteurs

        // Notification toast au lieu d'une alerte
        showToast('Jeu ajouté au panier !', 'success');

        // Réinitialiser le bouton après l'animation
        setTimeout(() => {
            button.classList.remove('adding');
            button.disabled = false;
        }, 1000);
    } catch (error) {
        console.error('Error adding to cart:', error);
        showToast('Erreur lors de l\'ajout au panier', 'error');
    }
}

// Fonction pour ajouter aux favoris depuis la page des jeux
function addToFavoritesFromGame(event) {
    try {
        const button = event.target.closest('.addToFavorites');
        if (!button) return;

        const card = button.closest('.card');
        if (!card) throw new Error('Card not found');

        const name = card.querySelector('.cardName')?.textContent;
        const image = card.querySelector('.cardImg img')?.src;
        const priceText = card.querySelector('.price')?.textContent;

        if (!name || !image) {
            throw new Error('Invalid game data');
        }

        const price = parseFloat(priceText.replace('€', ''));

        // Animation du bouton
        button.classList.add('adding');
        button.disabled = true;

        if (!favorites.some(item => item.name === name)) {
            favorites.push({
                name,
                image,
                price
            });
            localStorage.setItem('favorites', JSON.stringify(favorites));
            updateHeaderCounters(); // Mettre à jour les compteurs
            showToast('Jeu ajouté aux favoris !', 'success');
        } else {
            showToast('Ce jeu est déjà dans vos favoris !', 'info');
        }

        // Réinitialiser le bouton après l'animation
        setTimeout(() => {
            button.classList.remove('adding');
            button.disabled = false;
        }, 1000);
    } catch (error) {
        console.error('Error adding to favorites:', error);
        showToast('Erreur lors de l\'ajout aux favoris', 'error');
    }
}

// Fonction pour afficher une notification toast
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Animation d'entrée
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });

    // Supprimer après 3 secondes
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Fonction pour mettre à jour le panier
function updateCart() {
    const cartItems = document.getElementById('cartItems');
    const emptyCart = document.getElementById('emptyCart');
    
    if (!cartItems) return;

    if (cart.length === 0) {
        if (cartItems.parentElement && emptyCart) {
            cartItems.parentElement.classList.add('hidden');
            emptyCart.classList.remove('hidden');
        }
        return;
    }

    if (cartItems.parentElement && emptyCart) {
        cartItems.parentElement.classList.remove('hidden');
        emptyCart.classList.add('hidden');
    }
    
    cartItems.innerHTML = '';
    let subtotal = 0;

    cart.forEach((item, index) => {
        subtotal += item.price * item.quantity;
        
        const cartItem = document.createElement('div');
        cartItem.className = 'cart-item';
        cartItem.innerHTML = `
            <img src="${item.image}" alt="${item.name}">
            <div class="cart-item-info">
                <h3 class="cart-item-title">${item.name}</h3>
                <div class="cart-item-price">€${item.price.toFixed(2)}</div>
                <div class="cart-item-quantity">
                    <button class="quantity-btn" onclick="updateQuantity(${index}, -1)">-</button>
                    <span>${item.quantity}</span>
                    <button class="quantity-btn" onclick="updateQuantity(${index}, 1)">+</button>
                </div>
                <div class="cart-item-actions">
                    <button class="btn outline" onclick="removeFromCart(${index})">
                        <i class="fas fa-trash"></i> Supprimer
                    </button>
                    <button class="btn outline" onclick="addToFavorites(${index})">
                        <i class="fas fa-heart"></i> Favoris
                    </button>
                </div>
            </div>
        `;
        cartItems.appendChild(cartItem);
    });

    // Mise à jour du résumé
    const tax = subtotal * 0.2; // TVA 20%
    const total = subtotal + tax;

    const subtotalElement = document.getElementById('subtotalPrice');
    const taxElement = document.getElementById('taxAmount');
    const totalElement = document.getElementById('totalPrice');

    if (subtotalElement) subtotalElement.textContent = `€${subtotal.toFixed(2)}`;
    if (taxElement) taxElement.textContent = `€${tax.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `€${total.toFixed(2)}`;

    // Sauvegarder dans localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Fonction pour mettre à jour les compteurs du header
function updateHeaderCounters() {
    const cartCount = document.querySelector('.cartCount');
    const favCount = document.querySelector('.favCount');
    
    if (cartCount) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
        cartCount.style.display = totalItems > 0 ? 'flex' : 'none';
    }
    
    if (favCount) {
        favCount.textContent = favorites.length;
        favCount.style.display = favorites.length > 0 ? 'flex' : 'none';
    }
}

// Fonction pour mettre à jour la quantité
function updateQuantity(index, change) {
    const item = cart[index];
    const newQuantity = item.quantity + change;
    
    if (newQuantity > 0) {
        item.quantity = newQuantity;
        updateCart();
    } else if (newQuantity === 0) {
        removeFromCart(index);
    }
}

// Fonction pour supprimer du panier
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCart();
    updateHeaderCounters(); // Mettre à jour les compteurs
}

// Fonction pour ajouter aux favoris depuis le panier
function addToFavorites(cartIndex) {
    const item = cart[cartIndex];
    const existingIndex = favorites.findIndex(f => f.name === item.name);
    
    if (existingIndex === -1) {
        favorites.push({
            name: item.name,
            price: item.price,
            image: item.image
        });
        localStorage.setItem('favorites', JSON.stringify(favorites));
        showToast('Article ajouté aux favoris !', 'success');
    } else {
        showToast('Cet article est déjà dans vos favoris !', 'info');
    }
}

// Fonction pour mettre à jour les favoris
function updateFavorites() {
    const favoriteItemsContainer = document.getElementById('favoriteItems');
    if (!favoriteItemsContainer) return;

    favoriteItemsContainer.innerHTML = '';

    if (favorites.length === 0) {
        favoriteItemsContainer.innerHTML = '<p class="emptyFavorites">Vous n\'avez pas encore de favoris</p>';
        return;
    }

    favorites.forEach((item, index) => {
        const favoriteItem = document.createElement('div');
        favoriteItem.classList.add('favoriteItem');
        
        favoriteItem.innerHTML = `
            <img src="${item.image}" alt="${item.name}" />
            <div class="favoriteItemInfo">
                <h3>${item.name}</h3>
                <button class="removeFavoriteBtn" onclick="removeFromFavorites(${index})">
                    <i class="fas fa-trash"></i> Retirer des favoris
                </button>
            </div>
        `;
        favoriteItemsContainer.appendChild(favoriteItem);
    });
}

// Fonction pour supprimer des favoris
function removeFromFavorites(index) {
    favorites.splice(index, 1);
    localStorage.setItem('favorites', JSON.stringify(favorites));
    updateFavorites();
    updateHeaderCounters(); // Mettre à jour les compteurs
}

// Fonction pour afficher les favoris
function displayFavorites() {
    const favoriteItems = document.getElementById('favoriteItems');
    const emptyState = document.getElementById('emptyFavorites');
    
    // Récupérer les favoris du localStorage
    const favorites = JSON.parse(localStorage.getItem('favorites')) || [];
    
    // Vider le conteneur
    favoriteItems.innerHTML = '';
    
    if (favorites.length === 0) {
        // Afficher le message d'état vide
        emptyState.style.display = 'block';
        return;
    }
    
    // Cacher le message d'état vide
    emptyState.style.display = 'none';
    
    // Afficher chaque jeu favori
    favorites.forEach(game => {
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card';
        gameCard.innerHTML = `
            <div class="cardImg">
                <img src="${game.image}" alt="${game.name}">
                <span class="platform-tag">${game.platform}</span>
            </div>
            <div class="cardInfo">
                <p class="genre">${game.genre}</p>
                <h3 class="cardName">${game.name}</h3>
                <div class="card-details">
                    <div class="price">${game.price}</div>
                    <div class="card-actions">
                        <button class="btn addToCart" onclick="addToCart(event)" data-game='${JSON.stringify(game)}'>
                            <i class="fas fa-shopping-cart"></i> Ajouter
                        </button>
                        <button class="btn remove-favorite" onclick="removeFromFavorites('${game.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        favoriteItems.appendChild(gameCard);
    });
}

// Fonction pour supprimer un jeu des favoris
function removeFromFavorites(gameId) {
    let favorites = JSON.parse(localStorage.getItem('favorites')) || [];
    favorites = favorites.filter(game => game.id !== gameId);
    localStorage.setItem('favorites', JSON.stringify(favorites));
    
    // Mettre à jour l'affichage
    displayFavorites();
    
    // Afficher une notification
    showToast('Jeu retiré des favoris');
}

// Fonction pour afficher une notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    updateHeaderCounters(); // Mettre à jour les compteurs au chargement
    updateCart();
    updateFavorites();

    // Ajout des écouteurs d'événements
    document.querySelectorAll('.addToCart').forEach(button => {
        button.addEventListener('click', addToCart);
    });

    document.querySelectorAll('.addToFavorites').forEach(button => {
        button.addEventListener('click', addToFavoritesFromGame);
    });

    if (window.location.pathname.includes('favorites.html')) {
        displayFavorites();
    }
});
function showToast() {
    const toast = document.getElementById('toast');
    toast.classList.remove('hidden');
    toast.classList.add('show');
  
    // Masquer le toast après 3 secondes
    setTimeout(() => {
      toast.classList.remove('show');
      toast.classList.add('hidden');
    }, 3000);
  }
  
  // Exemple : Ajouter un événement au bouton "Ajouter au panier"
  const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
  addToCartButtons.forEach(button => {
    button.addEventListener('click', showToast);
  });