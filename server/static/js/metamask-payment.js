/**
 * MetaMask Payment Module
 *
 * Polygon 네트워크에서 USDC/USDT ERC-20 토큰 결제를 처리합니다.
 * ethers.js CDN이 페이지에 로드되어 있어야 합니다.
 *   <script src="https://cdn.jsdelivr.net/npm/ethers@6/dist/ethers.umd.min.js"></script>
 */

const ERC20_ABI = [
    "function transfer(address to, uint256 amount) returns (bool)",
];

const POLYGON_CHAIN_ID = "0x89";

const POLYGON_NETWORK_PARAMS = {
    chainId: POLYGON_CHAIN_ID,
    chainName: "Polygon Mainnet",
    nativeCurrency: {
        name: "MATIC",
        symbol: "POL",
        decimals: 18,
    },
    rpcUrls: ["https://polygon-rpc.com/"],
    blockExplorerUrls: ["https://polygonscan.com/"],
};

const TOKENS = {
    USDC: {
        address: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        decimals: 6,
    },
    USDT: {
        address: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        decimals: 6,
    },
};

/**
 * MetaMask 설치 여부를 확인합니다.
 * @returns {boolean}
 */
function isMetaMaskInstalled() {
    return typeof window.ethereum !== "undefined" && window.ethereum.isMetaMask;
}

/**
 * MetaMask에 연결하고 첫 번째 계정 주소를 반환합니다.
 * @returns {Promise<string>} 연결된 지갑 주소 (0x...)
 * @throws {Error} MetaMask 미설치 또는 사용자 거부 시
 */
async function connectMetaMask() {
    if (!isMetaMaskInstalled()) {
        throw new Error(
            "MetaMask가 설치되어 있지 않습니다. https://metamask.io 에서 설치해주세요."
        );
    }

    const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
    });

    if (!accounts || accounts.length === 0) {
        throw new Error("MetaMask 연결이 거부되었습니다.");
    }

    return accounts[0];
}

/**
 * 현재 네트워크가 Polygon인지 확인하고, 아니면 전환합니다.
 * @returns {Promise<void>}
 * @throws {Error} 네트워크 전환 실패 시
 */
async function switchToPolygon() {
    const currentChainId = await window.ethereum.request({
        method: "eth_chainId",
    });

    if (currentChainId === POLYGON_CHAIN_ID) {
        return;
    }

    try {
        await window.ethereum.request({
            method: "wallet_switchEthereumChain",
            params: [{ chainId: POLYGON_CHAIN_ID }],
        });
    } catch (switchError) {
        // 4902: 체인이 MetaMask에 추가되지 않은 경우
        if (switchError.code === 4902) {
            await window.ethereum.request({
                method: "wallet_addEthereumChain",
                params: [POLYGON_NETWORK_PARAMS],
            });
        } else {
            throw new Error(
                "Polygon 네트워크로 전환할 수 없습니다: " + switchError.message
            );
        }
    }
}

/**
 * MetaMask를 통해 ERC-20 토큰 결제를 실행합니다.
 *
 * @param {string} toAddress - 수신자 지갑 주소 (0x + 40자 hex)
 * @param {string} token - 토큰 심볼 ("USDC" 또는 "USDT")
 * @param {number|string} amount - 결제 금액 (사람이 읽는 단위, 예: 1.5 = 1.5 USDC)
 * @returns {Promise<string>} 트랜잭션 해시
 * @throws {Error} 결제 실패 시
 */
async function payWithMetaMask(toAddress, token, amount) {
    // 토큰 검증
    const tokenInfo = TOKENS[token.toUpperCase()];
    if (!tokenInfo) {
        throw new Error(
            "지원하지 않는 토큰입니다: " +
                token +
                ". USDC 또는 USDT만 지원합니다."
        );
    }

    // 주소 검증
    if (!toAddress || !/^0x[0-9a-fA-F]{40}$/.test(toAddress)) {
        throw new Error("유효하지 않은 지갑 주소입니다: " + toAddress);
    }

    // 금액 검증
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
        throw new Error("유효하지 않은 금액입니다: " + amount);
    }

    // 1. MetaMask 연결
    await connectMetaMask();

    // 2. Polygon 네트워크 확인/전환
    await switchToPolygon();

    // 3. ethers.js Provider + Signer 설정
    const provider = new window.ethers.BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();

    // 4. ERC-20 컨트랙트 인스턴스
    const contract = new window.ethers.Contract(
        tokenInfo.address,
        ERC20_ABI,
        signer
    );

    // 5. 금액을 토큰 단위로 변환 (decimals 적용)
    const parsedAmount = window.ethers.parseUnits(
        String(amount),
        tokenInfo.decimals
    );

    // 6. transfer 실행
    const tx = await contract.transfer(toAddress, parsedAmount);

    // 7. 트랜잭션 해시 반환
    return tx.hash;
}

// window에 함수 노출
window.MetaMaskPayment = {
    isMetaMaskInstalled,
    connectMetaMask,
    switchToPolygon,
    payWithMetaMask,
    TOKENS,
    POLYGON_CHAIN_ID,
};
