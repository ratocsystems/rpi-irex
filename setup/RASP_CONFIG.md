## **学習リモコンのセットアップ**  
  
### **Raspberry Pi の環境設定**  
学習リモコンの使用にあたり、RaspberryPiで使用できるよう環境の構築をおこないます。
今回使用するOSは Raspbian Stretch（2017年12月）を使用しています。OSのセットアップがお済でない場合は「[こちら](../install/README.md)」のページから、手順に従ってインストール作業をおこなってください。  
※本製品をご使用いただく時期により、Raspbianのバージョンが異なる場合があります。  
コマンド仕様の変更などにより、本マニュアルとの操作が異なる可能性がありますので、あらかじめご了承ください。  

---

Raspberry Pi本体をHDMIケーブルでディスプレイと接続し起動します。  
デスクトップ画面が表示されたら、左上にある "スタートメニュー" から "設定" ⇒ "PaspberryPiの設定"を選択します。  
画面が開いたら、"ローカライゼーション"タブをクリックし、以下の設定をおこないます。  
設定後、再起動を促すメッセージが表示れれば再起動をおこなってください。  
<table>
  <tr>
    <td>ロケールの設定 言語</td>
    <td>ja（Japanese）</td>
  </tr>
  <tr>
    <td>文字セット</td>
    <td>UTF-8</td>
  </tr>
  <tr>
    <td>タイムゾーンの設定 地域</td>
    <td>JapanもしくはAsia</td>
  </tr>
  <tr>
    <td>位置</td>
    <td>- もしくは Tokyo</td>
  </tr>
  <tr>
    <td>キーボードの設定</td>
    <td>日本 日本語（OADG 109A）</td>
  </tr>
  <tr>
    <td>無線LANの国</td>
    <td>JP Japan</td>
  </tr>
</table>  

---

再起動後、ネットワークの設定をおこないます。無線接続の場合は画面右上にある「ネットワークアイコン（[ネットワーク未接続時の図柄はこちら](./img/disconnect_lan.png)）」をクリックし、接続したい機器のSSIDを選択します。  
パスワードを聞かれますので、接続パスワードを入力すれば接続が完了します。  
無線LAN接続が完了した場合のアイコンの図柄は[こちら](./img/wifi_lan.png)  
  
有線LANの場合は、LANケーブルをRaspberryPiに接続することでネットワーク接続が完了します。  
有線LAN接続が完了した場合のアイコンの図柄は[こちら](./img/wire_lan.png)  

---

次に、Raspbian を最新の状態にするために更新作業をおこないます。  
上部のツールバーから "LXTerminal"（[アイコンの図柄はこちら](./img/lx_icon.png)）を起動します。  
起動後、**"pi@raspberry:~$"** と書かれた画面（黒い画面）が表示されますので、以下の文字を入力します。  

`sudo apt-get -y update`  
  
文字入力後にリターンキーを押すと自動処理され、処理後に **"pi@raspberry:~$"** と書かれた画面へ戻ります。  
続けて以下の文字を入力します。  

`sudo apt-get -y upgrade`  
  
自動処理後は **"pi@raspberry:~$"** へ戻ります。これで更新作業は終了ですので、次のステップへ進みます。  

---

### **GPIO 40PINのUARTを有効にするための環境設定**  
  
Raspberry Pi の GPIO 40PINを用いた接続で、UART制御を行うための設定です。  
  
#### **a) シリアル設定の削除**  
"LXTerminal" を起動し、以下のコマンドを入力します。  
  
`sudo leafpad /boot/cmdline.txt`  

テキストエディタが開きますので、以下の文字列の中からシリアル設定の項目を削除したのち保存し、テキストエディタを終了します。  

| 太文字の部分を削除します |
|:---|
| dwc_otg.lpm_enable=0　**console=serial0, 115200**　console=tty1　root=/dev/mmcblk0p7　rootfstype=ext4　elevator=deadline　fsck.repair=yes　rootwait splash |  
  
| 太文字を削除した例 |
|:---|
| dwc_otg.lpm_enable=0　console=tty1　root=/dev/mmcblk0p7　rootfstype=ext4　elevator=deadline　fsck.repair=yes　rootwait splash | 
---

#### **b) シリアル設定のサービス停止**  
  
"LXTerminal"を起動し、**pi@raspberry:~$** の後に以下のコマンドを入力します。  
  
`sudo systemctl stop serial-getty@ttyS0.service`  
  
上記の文字列を入力後エンターキーを押し、続けて以下のコマンドを入力します。  
  
`sudo systemctl disable serial-getty@ttyS0.service`  
  
---

#### **c) UARTの登録設定**  
  
上記の処理が終われば、以下のコマンドを入力し、テキストエディタを起動します。  
  
`sudo leafpad /boot/config.txt`  
  
テキストエディタが開きますので、以下の文字列を行の最後に追加し保存します。  
  
| 以下の文字列を行の最後に追加してください |
|:---|
| enable_uart=1 |  
    
保存が終われば、アプリケーションをすべて閉じて再起動してください。  

---

### **リモコン基板の確認**  
  
本製品が Raspberry Pi 上で正しく認識しているかを確認します。  
ツールバーから"LxTerminal"を起動します。  
ターミナルが表示されたら **pi@raspberry:~$** 以下に文字列を入力してください。  

---

#### **GPIO 40PIN で接続した場合の確認方法**  
  
GPIO 40PINで接続した場合は、ターミナルから以下の文字列を入力してください。  
  
`more /proc/device-tree/hat/product`  

上記の文字を入力後エンターキーを押すことで、画面に **"Interfaced Renite Control Board RPi-IREX"** と表示されていれば、次に進みます。  

次に以下の文字列を入力してください。  
  
`more /proc/device-tree/hat/vendor`  

上記の文字を入力後エンターキーを押すことで、画面に **"RATOC Systems, Inc."** と表示されていれば、正常に認識されています。  
  
---

#### **USBで接続した場合の確認方法**  
  
USBで接続した場合は、ターミナルから以下の文字列を入力してください。  
  
`lsusb`  
上記文字列を入力後、表示された一覧の中に **"Bus xxx Device xxx: ID 0584;007a RATOC Systems, Inc."** とあれば正常に認識されています。  
  
---

以上で動作をさせるための基本設定は終了です。  
以降は、Pythonプログラム等を駆使し、リモコンを動作させてみてください。  
  
Pythonプログラムの解説されたサンプルコードページは「[こちら](../python/README.md)」