const API_CANDIDATES = window.location.hostname === "localhost"
    ? ["http://localhost:8000", "http://127.0.0.1:8000"]
    : ["http://127.0.0.1:8000", "http://localhost:8000"];

async function apiFetch(path, options = {}) {
    let lastError = null;
    for (const base of API_CANDIDATES) {
        try {
            const response = await fetch(`${base}${path}`, options);
            if (!response.ok) {
                lastError = new Error(`HTTP ${response.status} on ${base}${path}`);
                continue;
            }
            return response;
        } catch (err) {
            lastError = err;
        }
    }
    throw lastError || new Error("API unreachable");
}

let cart = JSON.parse(localStorage.getItem("cart") || "[]");
let favorites = JSON.parse(localStorage.getItem("favorites") || "[]");
const FALLBACK_PRODUCTS = [
    { name: "Minecraft", platform: "pc", genre: "Simulation", price: 14.99, stock: 25, visible: true, image: "images/pc_sim_1.png", badge: "bestseller" },
    { name: "ZOO PLANET", platform: "pc", genre: "Simulation", price: 64.99, stock: 8, visible: true, image: "images/pc_sim_2.png", badge: "hot" },
    { name: "Call Of Duty : WARZONE", platform: "pc", genre: "Action / Aventure", price: 29.99, stock: 15, visible: true, image: "images/pc_act_2.png", badge: "discount" },
    { name: "Football Manager 2025", platform: "pc", genre: "Sport", price: 24.49, stock: 12, visible: true, image: "images/pc_sp_1.png", badge: "discount" },
    { name: "Rocket League", platform: "pc", genre: "Sport", price: 22.99, stock: 20, visible: true, image: "images/pc_sp_2.png", badge: "bestseller" },
    { name: "FORTNITE", platform: "pc", genre: "Action / Aventure", price: 34.49, stock: 30, visible: true, image: "images/pc_act_1.png", badge: null },
    { name: "Clair Obscur: Expedition 33", platform: "pc", genre: "Action / Aventure", price: 29.99, stock: 6, visible: true, image: "images/pc_act_3.png", badge: "new" },
    { name: "ARK : Survival Ascended", platform: "xbox", genre: "Action / Aventure", price: 34.99, stock: 10, visible: true, image: "images/xbox_act_1.png", badge: "new" },
    { name: "MADDEN NFL 25 Xbox", platform: "xbox", genre: "Sport", price: 39.99, stock: 14, visible: true, image: "images/xbox_sp_3.png", badge: "hot" },
    { name: "Grand Theft Auto V", platform: "xbox", genre: "Simulation", price: 22.49, stock: 16, visible: true, image: "images/xbox_sim_4.png", badge: "bestseller" },
    { name: "FORZZA MOTORSPORT", platform: "xbox", genre: "Sport", price: 59.99, stock: 9, visible: true, image: "images/xbox_sp_1.png", badge: "new" },
    { name: "EA SPORTS FC 24 Xbox", platform: "xbox", genre: "Sport", price: 69.99, stock: 7, visible: true, image: "images/xbox_sp_2.png", badge: null },
    { name: "ASTRONEER", platform: "xbox", genre: "Action / Aventure", price: 24.99, stock: 11, visible: true, image: "images/xbox_act_2.png", badge: "new" },
    { name: "Atomfall", platform: "xbox", genre: "Action / Aventure", price: 29.99, stock: 13, visible: true, image: "images/xbox_act_3.png", badge: null },
    { name: "ALIENS : DARK DESCENT", platform: "xbox", genre: "Action / Aventure", price: 19.99, stock: 9, visible: true, image: "images/xbox_act_4.png", badge: null },
    { name: "Farming Simulator 22", platform: "xbox", genre: "Simulation", price: 14.99, stock: 17, visible: true, image: "images/xbox_sim_1.png", badge: null },
    { name: "Disney Dreamlight Valley", platform: "xbox", genre: "Simulation", price: 44.99, stock: 10, visible: true, image: "images/xbox_sim_2.png", badge: "new" },
    { name: "Call of the Wild : The Angler", platform: "xbox", genre: "Simulation", price: 27.49, stock: 8, visible: true, image: "images/xbox_sim_3.png", badge: "new" },
    { name: "Death Stranding", platform: "ps5", genre: "Action / Aventure", price: 59.99, stock: 12, visible: true, image: "images/ps5_act_1.png", badge: "new" },
    { name: "God Of War", platform: "ps5", genre: "Action / Aventure", price: 24.99, stock: 22, visible: true, image: "images/ps5_act_3.png", badge: "bestseller" },
    { name: "The Last of Us", platform: "ps5", genre: "Action / Aventure", price: 39.99, stock: 18, visible: true, image: "images/ps5_act_2.png", badge: "bestseller" },
    { name: "EA Sports 25", platform: "ps5", genre: "Sport", price: 54.99, stock: 11, visible: true, image: "images/ps5_sp_1.png", badge: "discount" },
    { name: "Street Fighter 6", platform: "ps5", genre: "Sport", price: 39.99, stock: 14, visible: true, image: "images/ps5_sp_2.png", badge: "hot" },
    { name: "WWE 2K25", platform: "ps5", genre: "Sport", price: 49.99, stock: 10, visible: true, image: "images/ps5_sp_3.png", badge: null },
];

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function parsePrice(text) {
    const raw = String(text || "").replace(/[^\d.,-]/g, "").replace(",", ".");
    const parsed = parseFloat(raw);
    return Number.isFinite(parsed) ? parsed : 0;
}

function formatPrice(value) {
    return "EUR " + Number(value || 0).toFixed(2);
}

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(0)";
    });
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-20px)";
        setTimeout(() => toast.remove(), 300);
    }, 2400);
}

function syncStorage() {
    localStorage.setItem("cart", JSON.stringify(cart));
    localStorage.setItem("favorites", JSON.stringify(favorites));
}

function updateHeaderCounters() {
    const cartCount = document.querySelector(".cartCount");
    const favCount = document.querySelector(".favCount");
    if (cartCount) {
        const total = cart.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
        cartCount.textContent = String(total);
        cartCount.style.display = total > 0 ? "flex" : "none";
    }
    if (favCount) {
        favCount.textContent = String(favorites.length);
        favCount.style.display = favorites.length > 0 ? "flex" : "none";
    }
}

function addToCart(event) {
    const button = event?.target?.closest(".addToCart, .preorder-btn");
    if (!button) return;
    const card = button.closest(".card");
    if (!card) return;

    const name = card.querySelector(".cardName")?.textContent?.trim();
    const priceText = card.querySelector(".price")?.textContent;
    const image = card.querySelector(".cardImg img")?.getAttribute("src");
    const stockValue = parseInt(card.dataset.stock || "9999", 10);

    if (!name || !image) return;
    const price = parsePrice(priceText);
    const existing = cart.find((item) => item.name === name);

    if (existing) {
        if (existing.quantity >= stockValue) {
            showToast("Produit temporairement indisponible", "error");
            return;
        }
        existing.quantity += 1;
    } else {
        if (stockValue <= 0) {
            showToast("Produit temporairement indisponible", "error");
            return;
        }
        cart.push({ name, price, image, quantity: 1 });
    }

    syncStorage();
    updateCart();
    updateHeaderCounters();
    showToast("Jeu ajoute au panier", "success");
}

function addToFavoritesFromGame(event) {
    const button = event?.target?.closest(".addToFavorites");
    if (!button) return;
    const card = button.closest(".card");
    if (!card) return;

    const name = card.querySelector(".cardName")?.textContent?.trim();
    const priceText = card.querySelector(".price")?.textContent;
    const image = card.querySelector(".cardImg img")?.getAttribute("src");
    if (!name || !image) return;

    if (favorites.some((item) => item.name === name)) {
        showToast("Deja dans vos favoris", "info");
        return;
    }

    favorites.push({ name, image, price: parsePrice(priceText) });
    syncStorage();
    updateHeaderCounters();
    showToast("Ajoute aux favoris", "success");
}

function removeFromCart(index) {
    cart.splice(index, 1);
    syncStorage();
    updateCart();
    updateHeaderCounters();
}

function updateQuantity(index, diff) {
    const item = cart[index];
    if (!item) return;
    const next = item.quantity + diff;
    if (next <= 0) {
        removeFromCart(index);
        return;
    }
    item.quantity = next;
    syncStorage();
    updateCart();
    updateHeaderCounters();
}

function addToFavorites(cartIndex) {
    const item = cart[cartIndex];
    if (!item) return;
    if (!favorites.some((f) => f.name === item.name)) {
        favorites.push({ name: item.name, image: item.image, price: item.price });
        syncStorage();
        updateHeaderCounters();
    }
}

function removeFromFavorites(index) {
    favorites.splice(index, 1);
    syncStorage();
    updateFavorites();
    updateHeaderCounters();
}

function updateCart() {
    const cartItems = document.getElementById("cartItems");
    const emptyCart = document.getElementById("emptyCart");
    if (!cartItems) return;

    if (cart.length === 0) {
        cartItems.innerHTML = "";
        if (cartItems.parentElement && emptyCart) {
            cartItems.parentElement.classList.add("hidden");
            emptyCart.classList.remove("hidden");
        }
        const totalNode = document.getElementById("totalPrice");
        if (totalNode) totalNode.textContent = formatPrice(0);
        return;
    }

    if (cartItems.parentElement && emptyCart) {
        cartItems.parentElement.classList.remove("hidden");
        emptyCart.classList.add("hidden");
    }

    let total = 0;
    cartItems.innerHTML = cart
        .map((item, index) => {
            const line = Number(item.price) * Number(item.quantity);
            total += line;
            return `
                <div class="cart-item">
                    <img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.name)}" class="cart-item-image">
                    <div class="cart-item-details">
                        <h3>${escapeHtml(item.name)}</h3>
                        <div class="cart-item-price">${formatPrice(item.price)}</div>
                        <div class="cart-item-quantity">
                            <button onclick="updateQuantity(${index}, -1)" class="quantity-btn"><i class="fas fa-minus"></i></button>
                            <span>${item.quantity}</span>
                            <button onclick="updateQuantity(${index}, 1)" class="quantity-btn"><i class="fas fa-plus"></i></button>
                        </div>
                    </div>
                    <div class="cart-item-actions">
                        <button onclick="addToFavorites(${index})" class="btn outline"><i class="fas fa-heart"></i></button>
                        <button onclick="removeFromCart(${index})" class="btn outline delete"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            `;
        })
        .join("");

    const totalNode = document.getElementById("totalPrice");
    if (totalNode) totalNode.textContent = formatPrice(total);
}

function updateFavorites() {
    const favoriteItems = document.getElementById("favoriteItems");
    const emptyState = document.getElementById("emptyFavorites");
    if (!favoriteItems) return;

    favoriteItems.innerHTML = "";
    if (favorites.length === 0) {
        if (emptyState) emptyState.style.display = "block";
        return;
    }

    if (emptyState) emptyState.style.display = "none";
    favorites.forEach((game, index) => {
        const gameCard = document.createElement("div");
        gameCard.className = "game-card";
        gameCard.innerHTML = `
            <div class="cardImg"><img src="${escapeHtml(game.image)}" alt="${escapeHtml(game.name)}"></div>
            <div class="cardInfo">
                <h3 class="cardName">${escapeHtml(game.name)}</h3>
                <div class="card-details">
                    <div class="price">${formatPrice(game.price)}</div>
                    <div class="card-actions">
                        <button class="btn addToCart"><i class="fas fa-shopping-cart"></i> Ajouter</button>
                        <button class="btn remove-favorite" onclick="removeFromFavorites(${index})"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
            </div>
        `;
        favoriteItems.appendChild(gameCard);
    });

    favoriteItems.querySelectorAll(".addToCart").forEach((button) => {
        button.addEventListener("click", addToCart);
    });
}

function loadHeader() {
    fetch("header.html")
        .then((response) => response.text())
        .then((html) => {
            const temp = document.createElement("div");
            temp.innerHTML = html;
            const header = temp.querySelector(".headerContainer");
            if (!header) return;
            const oldHeader = document.querySelector(".headerContainer");
            if (oldHeader) oldHeader.replaceWith(header);
            else document.body.insertBefore(header, document.body.firstChild);
            updateHeaderCounters();
            updateHeaderUser();
        })
        .catch(() => {});
}

async function updateHeaderUser() {
    const token = localStorage.getItem("token");
    const logoutBtn = document.querySelector(".logout-btn");
    const signInBtn = document.querySelector(".headerLinks .signin-btn");

    if (!token) {
        if (logoutBtn) logoutBtn.style.display = "none";
        return;
    }

    try {
        const response = await apiFetch("/api/users/me", {
            headers: { Authorization: `Bearer ${token}` },
        });
        const data = await response.json();
        const username = data.username || data.email || "Compte";
        localStorage.setItem("username", username);
        if (signInBtn) {
            signInBtn.textContent = username.length > 14 ? username.slice(0, 14) : username;
            signInBtn.href = "profile.html";
            signInBtn.classList.add("logged-in");
            signInBtn.title = username;
        }
        if (logoutBtn) {
            logoutBtn.style.display = "inline-block";
            logoutBtn.onclick = (e) => {
                e.preventDefault();
                localStorage.removeItem("token");
                localStorage.removeItem("username");
                window.location.href = "signin.html";
            };
        }
    } catch (_err) {
        localStorage.removeItem("token");
        localStorage.removeItem("username");
    }
}

async function loadPlatformProducts() {
    const platform = document.body.dataset.platform;
    const container = document.getElementById("platformGamesContainer");
    if (!platform || !container) return;

    function renderProducts(products, warningMessage = "") {
        if (!products.length) {
            container.innerHTML = '<p class="empty-state">Aucun jeu disponible pour le moment.</p>';
            return;
        }

        container.innerHTML = `${warningMessage ? `<p class="small" style="grid-column:1/-1;color:#b45309;">${escapeHtml(warningMessage)}</p>` : ""}` + products
            .map((p) => {
                const badge = p.badge ? `<span class="badge ${escapeHtml(p.badge)}">${escapeHtml(p.badge)}</span>` : "";
                const isOut = Number(p.stock) <= 0;
                return `
                    <div class="card game-card" data-stock="${Number(p.stock)}">
                        <div class="cardImg">
                            <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}">
                            <div class="card-badges">${badge}</div>
                        </div>
                        <div class="cardInfo">
                            <p class="genre">${escapeHtml(p.genre)}</p>
                            <h3 class="cardName">${escapeHtml(p.name)}</h3>
                                                        <div class="card-details">
                                <div class="price">${formatPrice(p.price)}</div>
                                <div class="card-actions">
                                    <button class="btn addToCart" ${isOut ? "disabled" : ""}>
                                        <i class="fas fa-shopping-cart"></i> ${isOut ? "Indisponible" : "Ajouter"}
                                    </button>
                                    <button class="btn outline addToFavorites">
                                        <i class="fas fa-heart"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            })
            .join("");

        container.querySelectorAll(".addToCart").forEach((button) => button.addEventListener("click", addToCart));
        container.querySelectorAll(".addToFavorites").forEach((button) => button.addEventListener("click", addToFavoritesFromGame));
    }

    try {
        const response = await apiFetch(`/api/products?platform=${encodeURIComponent(platform)}`);
        const products = await response.json();
        if (!products.length) {
            const fallback = FALLBACK_PRODUCTS.filter((p) => p.platform === platform && p.visible);
            renderProducts(fallback);
            return;
        }
        renderProducts(products);
    } catch (err) {
        const fallback = FALLBACK_PRODUCTS.filter((p) => p.platform === platform && p.visible);
        renderProducts(fallback);
    }
}

async function loadHomeProducts() {
    const path = (window.location.pathname || "").toLowerCase();
    const isHome = path.endsWith("/index.html") || path === "/" || path === "";
    if (!isHome) return;

    const grid = document.querySelector(".games-section .games-grid");
    if (!grid) return;

    function render(products, warningMessage = "") {
        if (!products.length) return;
        const metric = document.getElementById("metric-games");
        if (metric) metric.textContent = `${products.length}+`;
        grid.innerHTML = `${warningMessage ? `<p class="small" style="grid-column:1/-1;color:#b45309;">${escapeHtml(warningMessage)}</p>` : ""}` + products
            .slice(0, 12)
            .map((p) => {
                const badge = p.badge ? `<span class="badge ${escapeHtml(p.badge)}">${escapeHtml(p.badge)}</span>` : "";
                const isOut = Number(p.stock) <= 0;
                return `
                    <div class="card game-card" data-stock="${Number(p.stock)}">
                        <div class="cardImg">
                            <img src="${escapeHtml(p.image)}" alt="${escapeHtml(p.name)}">
                            <div class="card-badges">${badge}</div>
                            <span class="platform-tag">${escapeHtml((p.platform || "home").toUpperCase())}</span>
                        </div>
                        <div class="cardInfo">
                            <p class="genre">${escapeHtml(p.genre)}</p>
                            <h3 class="cardName">${escapeHtml(p.name)}</h3>
                                                        <div class="card-details">
                                <div class="price">${formatPrice(p.price)}</div>
                                <div class="card-actions">
                                    <button class="btn addToCart" ${isOut ? "disabled" : ""}>
                                        <i class="fas fa-shopping-cart"></i> ${isOut ? "Indisponible" : "Ajouter"}
                                    </button>
                                    <button class="btn outline addToFavorites"><i class="fas fa-heart"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            })
            .join("");

        grid.querySelectorAll(".addToCart").forEach((button) => button.addEventListener("click", addToCart));
        grid.querySelectorAll(".addToFavorites").forEach((button) => button.addEventListener("click", addToFavoritesFromGame));
    }

    try {
        // Priorite aux jeux explicitement affectes a l'accueil
        const homeResp = await apiFetch("/api/products?platform=home");
        const homeProducts = await homeResp.json();
        if (homeProducts.length) {
            render(homeProducts);
            return;
        }

        // Fallback: sinon afficher le catalogue global visible
        const response = await apiFetch("/api/products");
        const products = await response.json();
        if (!products.length) {
            render(FALLBACK_PRODUCTS.filter((p) => p.visible));
            return;
        }
        render(products);
    } catch (err) {
        render(FALLBACK_PRODUCTS.filter((p) => p.visible));
    }
}

function attachContactHandler() {
    const form = document.getElementById("contactForm");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
            name: document.getElementById("name")?.value || "",
            email: document.getElementById("email")?.value || "",
            subject: document.getElementById("subject")?.value || "",
            message: document.getElementById("message")?.value || "",
        };
        try {
            const response = await apiFetch("/api/contact", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            form.reset();
            showToast(data.message || "Message envoye", "success");
        } catch (err) {
            alert(`Erreur envoi contact: ${err.message}`);
        }
    });
}

function initRevealAnimations() {
    const revealSelectors = [
        ".heroSection",
        ".wow-hero",
        ".games-section",
        ".platforms-section",
        ".newsletterSection",
        ".about-card",
        ".value-card",
        ".team-member",
        ".info-card",
        ".contact-form",
        ".cart-summary",
        ".cart-item",
        ".game-card",
        ".platform-card",
        ".admin-wrap .card",
    ];

    const nodes = document.querySelectorAll(revealSelectors.join(","));
    nodes.forEach((el) => el.setAttribute("data-reveal", ""));

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    nodes.forEach((el, index) => {
        el.style.transitionDelay = `${Math.min(index * 30, 240)}ms`;
        observer.observe(el);
    });
}

function initCardTilt() {
    const interactiveCards = document.querySelectorAll(
        ".game-card, .platform-card, .value-card, .info-card, .team-member, .admin-wrap .card, .favorites-container .game-card"
    );

    interactiveCards.forEach((card) => {
        card.addEventListener("mousemove", (e) => {
            if (window.innerWidth < 900) return;
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width;
            const y = (e.clientY - rect.top) / rect.height;
            const rotateY = (x - 0.5) * 7;
            const rotateX = (0.5 - y) * 7;
            card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "";
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadHeader();
    updateHeaderCounters();
    updateCart();
    updateFavorites();
    loadHomeProducts();
    loadPlatformProducts();
    attachContactHandler();
    initRevealAnimations();
    initCardTilt();

    document.querySelectorAll(".addToCart, .preorder-btn").forEach((button) => button.addEventListener("click", addToCart));
    document.querySelectorAll(".addToFavorites").forEach((button) => button.addEventListener("click", addToFavoritesFromGame));
});

window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;
window.addToFavorites = addToFavorites;
window.removeFromFavorites = removeFromFavorites;

