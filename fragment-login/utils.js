const jsQR = require("jsqr");
const Jimp = require("jimp");

var blobExtractionScript = function (blobUrl) {
  console.log(arguments);
  var uri = arguments[0];
  var callback = arguments[arguments.length - 1];
  var toBase64 = function (buffer) {
    for (
      var r,
        n = new Uint8Array(buffer),
        t = n.length,
        a = new Uint8Array(4 * Math.ceil(t / 3)),
        i = new Uint8Array(64),
        o = 0,
        c = 0;
      64 > c;
      ++c
    )
      i[c] =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(
          c
        );
    for (c = 0; t - (t % 3) > c; c += 3, o += 4)
      (r = (n[c] << 16) | (n[c + 1] << 8) | n[c + 2]),
        (a[o] = i[r >> 18]),
        (a[o + 1] = i[(r >> 12) & 63]),
        (a[o + 2] = i[(r >> 6) & 63]),
        (a[o + 3] = i[63 & r]);
    return (
      t % 3 === 1
        ? ((r = n[t - 1]),
          (a[o] = i[r >> 2]),
          (a[o + 1] = i[(r << 4) & 63]),
          (a[o + 2] = 61),
          (a[o + 3] = 61))
        : t % 3 === 2 &&
          ((r = (n[t - 2] << 8) + n[t - 1]),
          (a[o] = i[r >> 10]),
          (a[o + 1] = i[(r >> 4) & 63]),
          (a[o + 2] = i[(r << 2) & 63]),
          (a[o + 3] = 61)),
      new TextDecoder("ascii").decode(a)
    );
  };
  var xhr = new XMLHttpRequest();
  xhr.responseType = "arraybuffer";
  xhr.onload = function () {
    callback(toBase64(xhr.response));
  };
  xhr.onerror = function () {
    callback(xhr.status);
  };
  xhr.open("GET", uri);
  xhr.send();
};

async function readQRCode(buffer) {
  const image = await Jimp.read(buffer);
  const qr = new jsQR(
    image.bitmap.data,
    image.bitmap.width,
    image.bitmap.height
  );
  return qr.data;
}

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

exports.blobExtractionScript = blobExtractionScript;
exports.readQRCode = readQRCode;
exports.sleep = sleep;
