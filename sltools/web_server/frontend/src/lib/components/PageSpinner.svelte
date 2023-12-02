<!-- HTML -->
<div class="loading-message">
    <div class="loading-symbol">
        <img alt="" class="radiation-symbol" src="/common/radiation.svg"/>
    </div>
    <p>Loading...</p>
</div>

<!-- JS -->


<!-- CSS -->
<style>
    .loading-message {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        z-index: 9999;
    }

    img {
        width: 200px;
        height: 200px;
    }

    .loading-symbol {
        display: flex;
        justify-content: center;
        align-items: center;
        animation: rotation 2s linear infinite, pulse 1.5s infinite;
    }

    p {
        font-size: 20pt;
        color: #fff; /* Text color */
        margin: 20px 20px 10px;
    }

    @keyframes pulse {
        0% {
            transform: scale(1);
            rotate: 0deg;
        }
        50% {
            transform: scale(1.1);
        }
        100% {
            transform: scale(1);
            rotate: 360deg;
        }
    }
</style>
