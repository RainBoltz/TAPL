# General Fragment.com Login Example

This example shows how to login to Fragment.com programmatically using [Selenium](https://www.selenium.dev/) and [Node.js](https://nodejs.org/en/) **_WITHOUT [TONKEEPER](https://tonkeeper.com/)_**.

> Note: This is just a script that you can run to login to Fragment.com with random wallet everytime automaically. It is not a full application. You can use this script as a reference to build your own application.

## Prerequisites

- [Node.js](https://nodejs.org/en/) >= 18 + [npm](https://www.npmjs.com/get-npm)
- Safari browser + [Allow remote automation](https://developer.apple.com/documentation/webkit/testing_with_webdriver_in_safari#enable_remote_automation) (Chrome sucks after v114)
  > instructions: Choose `Safari` > `Preferences`, and on the `Advanced` tab, select `Show Develop menu in menu bar`, then choose `Develop` > `Allow Remote Automation`.

## Setup

```bash
$ cd fragment-login
$ npm install
```

## Run

```bash
$ cd fragment-login
$ npm run test
```
