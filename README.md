<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>


[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/AudricSerador/FightMyNebbies">
    <img src="static/logo.png" alt="Logo" width="180" height="180">
  </a>

  <h3 align="center">Fight My Nebbies</h3>

  <p align="center">
    A fun, interactive gacha-like Discord bot inspired by the old website <i>Fight My Monster</i> featuring RPG mechanics, including PvP, monster ("Nebby") customization, minigames and more!
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## Features
The bot currently has a variety of commands and features, including:

### Monster Creation
[![Image][showcase-1]](https://github.com/AudricSerador/FightMyNebbies)

### Monster PvP
[![Image][showcase-3]](https://github.com/AudricSerador/FightMyNebbies)
[![Image][showcase-2]](https://github.com/AudricSerador/FightMyNebbies)
[![Image][showcase-4]](https://github.com/AudricSerador/FightMyNebbies)

### Monster Artifacts
[![Image][showcase-5]](https://github.com/AudricSerador/FightMyNebbies)
[![Image][showcase-6]](https://github.com/AudricSerador/FightMyNebbies)

### Goofy Minigames
[![Image][showcase-7]](https://github.com/AudricSerador/FightMyNebbies)
[![Image][showcase-8]](https://github.com/AudricSerador/FightMyNebbies)

...and many more to come.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Built With

This bot was built with Python using the Discord.py library, with MySQL as the local database hosted through WampServer and managed through phpMyAdmin.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Discord.py](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![WampServer](https://img.shields.io/badge/WampServer-pink?style=for-the-badge&logo=https://upload.wikimedia.org/wikipedia/commons/4/4f/WampServer.png)


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Hosting The Bot

### Prerequisites
* Python (3.9 or later) - [Download](https://www.python.org/downloads/)
* WampServer (For local hosting) - [Download](https://www.wampserver.com/en/download-wampserver-64bits/)
* Newly created Discord bot - [How to setup a bot on Discord](https://discordpy.readthedocs.io/en/stable/discord.html)

### Installation and Setup
1. Clone the repo.
   ```sh
   git clone https://github.com/AudricSerador/FightMyNebbies
   ```
2. Install project dependencies
    ```sh
    pip install -r requirements.txt
    ```
3. Create a new file in the folder called `.env`. Set a variable `DISCORD_TOKEN` equal to your discord bot token.
4. Run WampServer on your device. This should take a few seconds.
5. In a new browser tab, navigate to `localhost/phpmyadmin`, you should see a login page to phpMyAdmin. The username is `root`, leave password empty. Log into the MySQL database.
6. Click on the "New" button to create a new database. Name it `discordrpg`.
![Image][tutorial-1]
7. Once created, navigate to the "SQL" tab at the top, and paste the SQL query in `discordrpg.sql` inside the repository folder. Click "Go".
![Image][tutorial-2]
8. Run `main.py`. Enjoy the bot!
![Image][tutorial-3]
<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt


[showcase-1]: static/showcase1.png
[showcase-2]: static/showcase2.png
[showcase-3]: static/showcase3.png
[showcase-4]: static/showcase4.png
[showcase-5]: static/showcase5.png
[showcase-6]: static/showcase6.png
[showcase-7]: static/showcase7.png
[showcase-8]: static/showcase8.png

[tutorial-1]: static/tutorial1.png
[tutorial-2]: static/tutorial2.png
[tutorial-3]: static/tutorial3.png