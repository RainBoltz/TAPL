const { TonLoginClient } = require("@tonapps/tonlogin-client");
const { mnemonicToWalletKey, mnemonicNew } = require("ton-crypto");
const { WalletContractV4 } = require("ton");
const { Builder, By } = require("selenium-webdriver");
const { blobExtractionScript, readQRCode, sleep } = require("./utils.js");

async function main() {
  /**
   * 0. open web page using Selenium
   */
  const driver = new Builder()
    .forBrowser("safari") // chromedriver with version > 114 is now unavailable
    .setChromeOptions()
    .build();

  await driver.get("https://fragment.com");
  await sleep(1000);

  /**
   * 1. get deeplink
   * (VERY TRICKY, YOU DON'T NEED TO UNDERSTAND THIS PART)
   */
  const loginBtns = await driver.findElements(
    By.xpath("//button[contains(@class, 'ton-auth-link')]")
  );
  for (let i = 0; i < loginBtns.length; i++) {
    try {
      await loginBtns[i].click();
      break;
    } catch (e) {
      // ignore ElementNotInteractableError
    }
  }

  await sleep(3000); // wait a sec for QR.showPopup() to be called

  const imgEle = await driver.findElement(
    By.xpath("//div[@class='tm-qr-code-image']")
  );
  const imgEleSrc = await imgEle.getAttribute("style");
  const imgEleUrl = imgEleSrc.split('"')[1];

  // get qrcode from blob url then convert to Base64
  const qrcodeBase64 = await driver.executeAsyncScript(
    blobExtractionScript,
    imgEleUrl
  );

  // scan qrcodeBase64
  const buffer = Buffer.from(qrcodeBase64, "base64");

  const deeplink = await readQRCode(buffer);
  console.log(`deeplink: ${deeplink}`);

  /**
   * 2. get 'Auth Request' from deeplink
   */
  const reqUrl = deeplink.replace("app.tonkeeper.com/ton-login/", "");
  const request = await fetch(reqUrl).then((res) => res.json());

  /**
   * 3. initialize wallet and settings
   * reference: https://github.com/tonkeeper/wallet/blob/develop/packages/mobile/src/core/TonConnect/TonConnectModal.tsx
   */
  const mnemonic = await mnemonicNew(24);
  const keys = await mnemonicToWalletKey(mnemonic);
  const fundingWallet = WalletContractV4.create({
    publicKey: keys.publicKey,
    workchain: 0,
  });

  const privateKey = keys.secretKey.toString("base64");
  const publicKey = keys.publicKey.toString("base64");
  const walletId = fundingWallet.walletId;
  const address = fundingWallet.address.toString({
    urlSafe: true,
    bounceable: true,
    testOnly: false,
  });
  const realm = "web";
  const service = "fragment.com";

  console.log(`Wallet ID: ${walletId}`);
  console.log(`Address: ${address}`);
  console.log(`Public Key: ${publicKey}`);
  console.log(`Private Key: ${privateKey}`);

  /**
   * 4. build payload and get response from tonlogin-server
   * reference: https://github.com/tonkeeper/ton-connect/blob/main/TonConnectSpecification.md
   */
  let signedHash = "";
  let callbackUrl = "";
  try {
    const tonlogin = new TonLoginClient(request);
    const response = await tonlogin.createResponse({
      service,
      seed: privateKey,
      realm,
      payload: {
        tonAddress: () => ({ address }),
        tonOwnership: ({ clientId }) => {
          const signature = tonlogin.createTonOwnershipSignature({
            secretKey: keys.secretKey,
            walletVersion: "v4R2",
            address,
            clientId,
          });

          return {
            wallet_version: "v4R2",
            wallet_id: walletId,
            pubkey: publicKey,
            address,
            signature,
          };
        },
      },
    });

    console.log(`tonlogin string: ${response}`);
    console.log(tonlogin.getRequestBody());

    signedHash = response;
    callbackUrl = tonlogin.getRequestBody().callback_url;
  } catch (error) {
    console.log(error);
  }

  /**
   * 5. send authenticated payload back to tonlogin-server
   * we will get verified on this step
   */
  const verUrl = new URL(`${callbackUrl}&tonlogin=${signedHash}`);
  const response = await fetch(verUrl, {
    method: "GET",
  }).then((res) => res.json());

  console.log(response);

  /**
   * 6. close browser after 30 seconds
   * [Optional]
   */
  await sleep(30000);
  await driver.quit();
}

main();
