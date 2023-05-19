<h1 align="center">
  Twitter Bot
</h1>
<p align="center">
  Automatic tweets for new FAANG engineering positions in Zürich.
</p>
![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?style=for-the-badge&logo=Twitter&logoColor=white)
<div align="center">
  <img src="https://raw.githubusercontent.com/oluevaera/TwitterBot/main/images/twitter_bot.png?token=GHSAT0AAAAAACBHMLO5KOMJZI4GVMKDMMV4ZDHZJ7A" alt="Image" />
</div>

## Description
If you are interested in a SWE or any other Engineering position in one of the Big-Tech companies in Zürich you should follow [@SWEJobAds](https://twitter.com/SWEJobAds)

## Information
Each of the company scripts are scrapping the career website of their respective company for new positions. 

* The scripts are running every 3 hours to check if there are new positions posted.
* The tweets have #hashtags in order for the users and the developer to have access to the positions by company.
* The data are collected with the "requests_html" Python library.
* The links are shortened with "pyshorteners" for better readability on the tweet.
