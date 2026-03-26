/**
 * MetaMask Payment Module
 *
 * Polygon 네트워크에서 USDC/USDT ERC-20 토큰 결제를 처리합니다.
 * ethers.js CDN이 페이지에 로드되어 있어야 합니다.
 *
 * 사용 전 window.POLYGON_CONFIG를 설정하세요:
 *   window.POLYGON_CONFIG = { chainId, chainName, rpcUrl, explorerUrl, currencySymbol, tokens }
 */

const ERC20_ABI = [
    "function transfer(address to, uint256 amount) returns (bool)",
];

function getConfig() {
    return window.POLYGON_CONFIG || {
        chainId: "0x89",
        chainName: "Polygon Mainnet",
        rpcUrl: "https://polygon-rpc.com/",
        explorerUrl: "https://polygonscan.com/",
        currencySymbol: "POL",
        tokens: {
            USDC: { address: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", decimals: 6 },
            USDT: { address: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", decimals: 6 },
        },
    };
}

function isMetaMaskInstalled() {
    return typeof window.ethereum !== "undefined" && (window.ethereum.isMetaMask || window.ethereum.providers?.some(p => p.isMetaMask));
}

function getMetaMaskProvider() {
    if (window.ethereum?.providers) {
        return window.ethereum.providers.find(p => p.isMetaMask) || window.ethereum;
    }
    return window.ethereum;
}

async function connectMetaMask() {
    if (!isMetaMaskInstalled()) {
        throw new Error("MetaMask가 설치되어 있지 않습니다. https://metamask.io 에서 설치해주세요.");
    }
    const provider = getMetaMaskProvider();
    const accounts = await provider.request({ method: "eth_requestAccounts" });
    if (!accounts || accounts.length === 0) {
        throw new Error("MetaMask 연결이 거부되었습니다.");
    }
    return accounts[0];
}

async function switchToPolygon() {
    const config = getConfig();
    const provider = getMetaMaskProvider();
    const currentChainId = await provider.request({ method: "eth_chainId" });

    if (currentChainId === config.chainId) return;

    try {
        await provider.request({
            method: "wallet_switchEthereumChain",
            params: [{ chainId: config.chainId }],
        });
    } catch (switchError) {
        if (switchError.code === 4902) {
            await provider.request({
                method: "wallet_addEthereumChain",
                params: [{
                    chainId: config.chainId,
                    chainName: config.chainName,
                    nativeCurrency: { name: "POL", symbol: config.currencySymbol, decimals: 18 },
                    rpcUrls: [config.rpcUrl],
                    blockExplorerUrls: [config.explorerUrl],
                }],
            });
        } else {
            throw new Error("네트워크 전환에 실패했습니다: " + switchError.message);
        }
    }
}

async function payWithMetaMask(toAddress, token, amount) {
    const config = getConfig();
    const tokenInfo = config.tokens[token.toUpperCase()];
    if (!tokenInfo) {
        throw new Error("지원하지 않는 토큰입니다: " + token);
    }
    if (!toAddress || !/^0x[0-9a-fA-F]{40}$/.test(toAddress)) {
        throw new Error("유효하지 않은 지갑 주소입니다.");
    }
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
        throw new Error("유효하지 않은 금액입니다.");
    }

    await connectMetaMask();
    await switchToPolygon();

    const mmProvider = getMetaMaskProvider();
    const ethProvider = new window.ethers.BrowserProvider(mmProvider);
    const signer = await ethProvider.getSigner();

    const contract = new window.ethers.Contract(tokenInfo.address, ERC20_ABI, signer);
    const parsedAmount = window.ethers.parseUnits(String(numAmount), tokenInfo.decimals);

    const tx = await contract.transfer(toAddress, parsedAmount);
    await tx.wait();
    return tx.hash;
}

window.MetaMaskPayment = {
    isMetaMaskInstalled,
    connectMetaMask,
    switchToPolygon,
    payWithMetaMask,
    getConfig,
};
