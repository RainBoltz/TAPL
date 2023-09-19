const { TonLoginClient, TonLoginClientError, CreateResponseOptions } = require('@tonapps/tonlogin-client');
const { mnemonicToWalletKey, mnemonicNew } = require("ton-crypto");
const { TonClient, WalletContractV4, internal } = require("ton");
const fs = require("fs");
const path = require("path");
const Jimp = require("jimp");
const qrCode = require('qrcode-reader');
const FileReader = require('filereader');


async function downloadImage(imageURL, dirPath = "./tmp", fileName = "image.png") {
    // Create the directory if it does not exist
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath);
    }

    // Use fetch to get the image data as a buffer
    const blob = await fetch(imageURL)
        .then(r => r.blob())
        .catch((err) => console.error(err));

    // write the file to the directory
    const fileReader = new FileReader();
    fileReader.onload = function () {
        fs.writeFileSync(path.join(dirPath, fileName), Buffer(new Uint8Array(this.result)));
    };
    fileReader.readAsArrayBuffer(blob);
}

function decodeQRCode(imagePath = './tmp/image.png') {
    const buffer = fs.readFileSync(imagePath);

    let value = "";
    // Parse the image using Jimp.read() method
    Jimp.read(buffer, function (err, image) {
        if (err) {
            console.error(err);
        }
        // Creating an instance of qrcode-reader module
        let qrcode = new qrCode();
        qrcode.callback = function (err, value) {
            if (err) {
                console.error(err);
            }
            // Printing the decrypted value
            console.log(value.result);
            value = value.result;
        };
        // Decoding the QR code
        qrcode.decode(image.bitmap);
    });

    return value;
}

async function sleep(ms = 0) {
    return new Promise(r => setTimeout(r, ms));
}

async function main() {

    //1. get deeplink from QR code
    const deeplink = "https://app.tonkeeper.com/ton-login/fragment.com/tonkeeper/authRequest?id=..." // extract from QR code

    //2. get Auth Request received from @tonapps/tonlogin-server
    const reqUrl = new URL(deeplink.replace('app.tonkeeper.com/ton-login/', ''));
    const request = await fetch(reqUrl).then(res => res.json());

    //3. initialize wallet and settings
    // (ref: https://github.com/tonkeeper/wallet/blob/develop/packages/mobile/src/core/TonConnect/TonConnectModal.tsx)

    const mnemonic = await mnemonicNew(24);
    const keys = await mnemonicToWalletKey(mnemonic);
    const fundingWallet = WalletContractV4.create({ publicKey: keys.publicKey, workchain: 0 });

    const privateKey = keys.secretKey.toString("base64");
    const publicKey = keys.publicKey.toString("base64");
    const walletId = fundingWallet.walletId;
    const address = fundingWallet.address.toString({ urlSafe: true, bounceable: true, testOnly: false });
    const realm = "web"
    const service = "fragment.com"

    console.log(`Wallet ID: ${walletId}`);
    console.log(`Address: ${address}`);
    console.log(`Public Key: ${publicKey}`);
    console.log(`Private Key: ${privateKey}`);

    //4. create request to @tonapps/tonlogin-server
    // (ref1: https://github.com/tonkeeper/ton-connect/blob/main/TonConnectSpecification.md)
    let signedHash = "";
    let callbackUrl = "";
    try {

        // If a validation error occurs, constructor throw exception.
        const tonlogin = new TonLoginClient(request);

        // Create response with payload
        const response = await tonlogin.createResponse({
            service,
            seed: privateKey,
            realm,
            payload: {
                tonAddress: () => ({ address }),
                tonOwnership: ({ clientId }) => {
                    const signature = tonlogin.createTonOwnershipSignature({
                        secretKey: keys.secretKey,
                        walletVersion: 'v4R2',
                        address,
                        clientId
                    })

                    return {
                        wallet_version: 'v4R2',
                        wallet_id: walletId,
                        pubkey: publicKey,
                        address,
                        signature,
                    }
                }
            }
        });


        console.log(`tonlogin string: ${response}`);
        console.log(tonlogin.getRequestBody());

        signedHash = response;
        callbackUrl = tonlogin.getRequestBody().callback_url;

    } catch (error) {
        console.log(error);
    }

    //5. send response to @tonapps/tonlogin-server
    const verUrl = new URL(`${callbackUrl}&tonlogin=${signedHash}`);
    const response = await fetch(verUrl, {
        method: 'GET',
    }).then(res => res.json());

    console.log(response);
}

main();
