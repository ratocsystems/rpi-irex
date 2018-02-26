#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import argparse
import json

import RPi.GPIO as GPIO #GPIO制御用

import serial   #シリアル制御用
from serial.tools import list_ports


#CRC計算
def crc8_calc(payload_buf, payload_length): 
    CRC8Table = [
    0x00, 0x85, 0x8F, 0x0A, 0x9B, 0x1E, 0x14, 0x91,
    0xB3, 0x36, 0x3C, 0xB9, 0x28, 0xAD, 0xA7, 0x22,
    0xE3, 0x66, 0x6C, 0xE9, 0x78, 0xFD, 0xF7, 0x72,
    0x50, 0xD5, 0xDF, 0x5A, 0xCB, 0x4E, 0x44, 0xC1,
    0x43, 0xC6, 0xCC, 0x49, 0xD8, 0x5D, 0x57, 0xD2,
    0xF0, 0x75, 0x7F, 0xFA, 0x6B, 0xEE, 0xE4, 0x61,
    0xA0, 0x25, 0x2F, 0xAA, 0x3B, 0xBE, 0xB4, 0x31,
    0x13, 0x96, 0x9C, 0x19, 0x88, 0x0D, 0x07, 0x82,

    0x86, 0x03, 0x09, 0x8C, 0x1D, 0x98, 0x92, 0x17,
    0x35, 0xB0, 0xBA, 0x3F, 0xAE, 0x2B, 0x21, 0xA4,
    0x65, 0xE0, 0xEA, 0x6F, 0xFE, 0x7B, 0x71, 0xF4,
    0xD6, 0x53, 0x59, 0xDC, 0x4D, 0xC8, 0xC2, 0x47,
    0xC5, 0x40, 0x4A, 0xCF, 0x5E, 0xDB, 0xD1, 0x54,
    0x76, 0xF3, 0xF9, 0x7C, 0xED, 0x68, 0x62, 0xE7,
    0x26, 0xA3, 0xA9, 0x2C, 0xBD, 0x38, 0x32, 0xB7,
    0x95, 0x10, 0x1A, 0x9F, 0x0E, 0x8B, 0x81, 0x04,

    0x89, 0x0C, 0x06, 0x83, 0x12, 0x97, 0x9D, 0x18,
    0x3A, 0xBF, 0xB5, 0x30, 0xA1, 0x24, 0x2E, 0xAB,
    0x6A, 0xEF, 0xE5, 0x60, 0xF1, 0x74, 0x7E, 0xFB,
    0xD9, 0x5C, 0x56, 0xD3, 0x42, 0xC7, 0xCD, 0x48,
    0xCA, 0x4F, 0x45, 0xC0, 0x51, 0xD4, 0xDE, 0x5B,
    0x79, 0xFC, 0xF6, 0x73, 0xE2, 0x67, 0x6D, 0xE8,
    0x29, 0xAC, 0xA6, 0x23, 0xB2, 0x37, 0x3D, 0xB8,
    0x9A, 0x1F, 0x15, 0x90, 0x01, 0x84, 0x8E, 0x0B,

    0x0F, 0x8A, 0x80, 0x05, 0x94, 0x11, 0x1B, 0x9E,
    0xBC, 0x39, 0x33, 0xB6, 0x27, 0xA2, 0xA8, 0x2D,
    0xEC, 0x69, 0x63, 0xE6, 0x77, 0xF2, 0xF8, 0x7D,
    0x5F, 0xDA, 0xD0, 0x55, 0xC4, 0x41, 0x4B, 0xCE,
    0x4C, 0xC9, 0xC3, 0x46, 0xD7, 0x52, 0x58, 0xDD,
    0xFF, 0x7A, 0x70, 0xF5, 0x64, 0xE1, 0xEB, 0x6E,
    0xAF, 0x2A, 0x20, 0xA5, 0x34, 0xB1, 0xBB, 0x3E,
    0x1C, 0x99, 0x93, 0x16, 0x87, 0x02, 0x08, 0x8D
    ]
    crc = 0
    for i in range(payload_length):
        crc = CRC8Table[(crc ^ payload_buf[i]) % 256]
    return crc

#シリアル送信
def output_irSerial(buf, irser):    
    payload_len =len(buf)
    payload_crc = crc8_calc(buf, payload_len)
    packet_data = []
    packet_data.append(0x7E)                        #SYNデータ(0x7E固定)
    packet_data.append(0xAA)                        #ヘッダー(0xAA固定)

    #ペイロードバイト数(HiByte)
    len_hi = (payload_len >> 8) & 0xFF              
    if len_hi == 0x7D or len_hi == 0x7E:            #SYN(0x7E)またはESC(0x7D)がある場合
        packet_data.append(0x7D)                    #ESC(0x7D)を追加して 
        packet_data.append(len_hi ^ 0x20)           #0x20で排他的論理和する
    else:
        packet_data.append(len_hi)                  #そのまま追加    
    #ペイロードバイト数(LoByte)
    len_lo = payload_len & 0xFF              
    if len_lo == 0x7D or len_lo == 0x7E:            #SYN(0x7E)またはESC(0x7D)がある場合
        packet_data.append(0x7D)                    #ESC(0x7D)を追加して 
        packet_data.append(len_lo ^ 0x20)           #0x20で排他的論理和する
    else:
        packet_data.append(len_lo)                  #そのまま追加    

    #ペイロードデータ作成
    for i in range(payload_len):
        if buf[i] == 0x7D or buf[i] == 0x7E:        #ペイロード内にSYN(0x7E)またはESC(0x7D)がある場合
            packet_data.append(0x7D)                #ESC(0x7D)を追加して 
            packet_data.append(buf[i] ^ 0x20)       #0x20で排他的論理和する
        else:
            packet_data.append(buf[i])              #そのまま追加

    #CRC追加
    if payload_crc == 0x7D or payload_crc == 0x7E:  #SYN(0x7E)またはESC(0x7D)がある場合
        packet_data.append(0x7D)                    #ESC(0x7D)を追加して 
        packet_data.append(payload_crc ^ 0x20)      #0x20で排他的論理和する
    else:
        packet_data.append(payload_crc)             #そのままCRC追加

    packet_data.append(0x7E)                        #SYNCコード(0x7E固定)

    irser.write(bytes(packet_data))

#シリアル受信
def input_irSerial(cmd, irser):    
    try:
        data = []
        #SYNデータ(0x7E)受信
        buf = irser.read()
        data.append(buf[0])
        if data[0] != 0x7E:
            print("受信データが正しくありません[0x7E:0x%X]" % data[0])
            irser.close()
            sys.exit()  #プログラム終了

        #ヘッダー(0xAA)受信
        buf = irser.read()
        data.append(buf[0])
        if data[1] != 0xAA:
            print("受信データが正しくありません[0xAA:0x%X]" % data[1])
            irser.close()
            sys.exit()  #プログラム終了
 
        #ペイロード数(Hi)
        buf = irser.read()
        if buf[0] == 0x7D:                 #ESC(0x7D)だった場合
            buf = irser.read()             #ESC(0x7D)を捨てて
            data.append(buf[0] ^ 0x20)    #次のデータと0x20で排他的論理和したものを保存
        else:
            data.append(buf[0])
        #ペイロード数(Lo)
        buf = irser.read()
        if buf[0] == 0x7D:                 #ESC(0x7D)だった場合
            buf = irser.read()             #ESC(0x7D)を捨てて
            data.append(buf[0] ^ 0x20)    #次のデータと0x20で排他的論理和したものを保存
        else:
            data.append(buf[0])
        #ペイロード数計算        
        payload_count = ((data[2]<<8) & 0xFF00) + data[3]

        #ペイロード, CRC, SYNを受信
        for i in range(payload_count+2):
            buf = irser.read()
            if buf[0] == 0x7D:                 #ESC(0x7D)だった場合
                buf = irser.read()             #ESC(0x7D)を捨てて
                data.append(buf[0] ^ 0x20)    #次のデータと0x20で排他的論理和したものを保存
            else:
                data.append(buf[0])

        #SYN(0x7E)確認
        if data[payload_count+5] != 0x7E:
            print("受信データが正しくありません[0x7E:0x%X]" % data[payload_count+5])
            irser.close()
            sys.exit()  #プログラム終了

        #ペイロードデータ保管
        payload_data = []
        for j in range(payload_count):
            payload_data.append(data[j+4]) 

        #CRC確認
        if data[payload_count+4] != crc8_calc(payload_data, payload_count):
            print("CRCが正しくありません")
            irser.close()
            sys.exit()  #プログラム終了
        else:
            return payload_data
    except:
        print("*** 受信に失敗しました") #受信に失敗しました
        irser.close()
        sys.exit()

#赤外線データ送信
def output_irData(irser, fileName):   
    verCmd = 0x01   #赤外線データ送信コマンド
    buf = []

    f = open(fileName, 'r')
    ir_file = json.load(f)
    f.close()


    buf.append(verCmd)                      #赤外線データ送信コマンド
    buf.append(ir_file['FormatType'])       #赤外線フォーマットタイプ

    ir_data_len = ir_file['DataLength']
    buf.append((ir_data_len >> 8) & 0xFF)   #赤外線送信バイト数 Hiバイト
    buf.append(ir_data_len & 0xFF)          #赤外線送信バイト数 Loバイト

    ir_data = ir_file['SignalData']
    for i in range(ir_data_len):
        buf.append(ir_data[i])

    output_irSerial(buf, irser)                         #コマンド送信
    payload_data = input_irSerial(verCmd, irser)    #応答受信

    #応答コード確認
    if payload_data[0] != verCmd:
        print("応答コードが正しくありません[0x%X:0x%X]" % (verCmd, payload_data[0]))
    #終了コード確認
    elif payload_data[1] != 0x00:
        print("正常に終了しませんでした:0x%X" % payload_data[1])
    else:     
        print("赤外線データは正常に送出されました:0x%X" % payload_data[1])

#ファームウェアバージョン取得
def get_fwVersion(irser):   
    verCmd = 0xD0   #ファームウェアバージョン取得コマンド
    buf = [verCmd]    

    output_irSerial(buf, irser)                  #コマンド送信
    payload_data = input_irSerial(verCmd, irser) #応答受信

    #応答コード確認
    if payload_data[0] != verCmd:
        print("応答コードが正しくありません[0x%X:0x%X]" % (verCmd, payload_data[0]))
    #終了コード確認
    elif payload_data[1] != 0x00:
        print("正常に終了しませんでした:0x%X" % payload_data[1])
    else:     
        mjr_ver = format(payload_data[2], '02x')
        mnr_ver = format(payload_data[3], '02x')

        s = 'Firmware Version:' + mjr_ver + '.' + mnr_ver
        print(s)

#RPi-IREXをリセット
def set_Reset():
    GPIO.setmode(GPIO.BOARD)    #GPIOピン番号モードに設定
    GPIO.setup(15,GPIO.OUT) #GPIO22(15pin)を出力に設定
    GPIO.output(15,False)   #GPIO22(15pin)をLo
    time.sleep(1.0)
    GPIO.output(15,True)   #GPIO22(15pin)をHi
    GPIO.cleanup()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                prog='irexOut.py',  #プログラムファイル名
                usage='RPi-IREXの使用方法',  #使用方法
                description='引数の説明----------------------------------------------------------------',
                epilog='--------------------------------------------------------------------------',
                add_help=True,
                )
    #引数
    parser.add_argument('-d', '--device', metavar='[DeviceFile]', nargs=1, help='RPi-IREXが接続されているデバイスファイルを指定 例)-d /dev/ttyS0')
    parser.add_argument('-f', '--file', metavar='[irDataFile]', nargs=1, help='赤外線信号を出力。出力する赤外線信号ファイルを指定 例)-f irData.json')
    parser.add_argument('-v', '--version', help='RPi-IREXのファームウェアバージョンを取得', action='store_true')
    parser.add_argument('-r', '--reset', help='RPi-IREXをリセット', action='store_true')

    args = parser.parse_args()  #引数確認

    #リセット
    if args.reset:
        print("RPi-IREXをリセットします")
        set_Reset()
        sys.exit()  #プログラム終了

    #RPi-IREX検索
    if args.device:    #デバイスファイル指定
        dev_file = args.device[0] #デバイスファイル名取得
        if os.path.exists(dev_file):    #RPi-IREXが接続されているか確認
            print("%sで制御を行います" % dev_file)
        else:
            print("*** %sが見つかりません" % dev_file)
            sys.exit()
    else:   #USB接続のRPi-IREXを自動検索
        try:
            temp = list_ports.grep("0584:007a") #RPi-IREXのVID:0584/PID:007Aで検索
            dev_file = list(temp)[0][0]
            print("USB接続のRPi-IREXが見つかりました:%s" % dev_file)
        except:
            print("*** USB接続のRPi-IREXが見つかりません") #USB接続のRPi-IREXが見つからなかった
            print("*** UART接続の場合、デバイスファイルを指定してください 例)-d /dev/ttyS0")
            sys.exit()

    #シリアル通信設定
    ser = serial.Serial(dev_file, 115200, timeout=5)

    if args.version:  #ファームウェアバージョン取得
        print('RPi-IREXのファームウェアバージョンを取得します')
        get_fwVersion(ser)
  
    if args.file:  #赤外線リモコンデータ送信
        print('赤外線リモコンデータを送信します')
        output_irData(ser, args.file[0])

    ser.close()
    sys.exit()
