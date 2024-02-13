from .requests import aiorequests
from .apscheduler import scheduler
from .database import get_all_subs_uid_did_token,From_alldata_del_uid,From_userid_del_data

import asyncio
import random
from nonebot.log import logger
host = 'https://api-cloudgame.mihoyo.com/'

cloud_genshin_enable = True
#自动签到开关

cloud_genshin_hour = 7
#云原神开始签到时间（小时）

@scheduler.scheduled_job('cron', hour=cloud_genshin_hour, misfire_grace_time=10)
async def _():
    # logger.info('云原神', f'开始执行云原神自动，共<m>{len(subs)}</m>个任务，预计花费<m>{round(75 * len(subs) / 60, 2)}</m>分钟')
    if not cloud_genshin_enable:
        #如果未打开自动签到开关
        return
    uid,did,token = get_all_subs_uid_did_token()
    acc_num=len(uid)
    if not uid:
        #如果无数据
        return
    success_count = 0
    faild_count = 0
    
    logger.info("云原神!",f"自动签到启!动! 共{acc_num}个账号")
    logger.info(f"预计本次签到需要花费{10 * acc_num / 60}分钟")
    for now_progress in range(acc_num):
        
        if await check_token(did[now_progress],token[now_progress]):
            info = await get_Info(uid[now_progress], token[now_progress])
            if info['data']['free_time']['free_time'] == 600:
                logger.info(f"{uid[now_progress]}签到失败 免费时长达到上限")
                success_count += 1
            else:
                sign = await get_Notification(did[now_progress], token[now_progress])
                msg = '云原神签到成功' if sign['data']['list'] else '云原神今日已签到'
                logger.success(f"{uid[now_progress]} {msg}")
                success_count +=1
        else:
            logger.error(f"{uid[now_progress]}的云原神token已失效")
            From_alldata_del_uid(uid[now_progress])
            faild_count += 1
            
        await asyncio.sleep(random.randint(3, 5))
    
    logger.success(f'云原神 ➤➤ 成功签到数{success_count}/{acc_num}')
    logger.success(f'云原神 ➤➤ 签到成功率{success_count / acc_num * 100}%')


async def get_hand_qd(user_id:str | None,uids,drive_ids,tokens):
    
    acc_num=len(uids)
    
    success_count = 0
    faild_count = 0
    result = ""
    
    for now_progress in range(acc_num):
        
        if await check_token(drive_ids[now_progress],tokens[now_progress]):
            info = await get_Info(drive_ids[now_progress], tokens[now_progress])
            if info['data']['free_time']['free_time'] == 600:
                logger.info(f"{uids[now_progress]}签到失败 免费时长达到上限")
                result += f"{uids[now_progress]} > 免费时长达到上限\n"
                success_count += 1
            else:
                sign = await get_Notification(drive_ids[now_progress], tokens[now_progress])
                msg = '云原神签到成功' if sign['data']['list'] else '云原神今日已签到'
                logger.success(f"{uids[now_progress]} {msg}")
                result += f"{uids[now_progress]} > {msg}\n"
                success_count +=1
        else:
            logger.error(f"{uids[now_progress]}的云原神token已失效")
            if not user_id:
                From_alldata_del_uid(uids[now_progress])
            else:
                From_userid_del_data(user_id,uids[now_progress])
            result += f"{uids[now_progress]} > 云原神token已失效,请重新绑定\n"
            faild_count += 1
            
        await asyncio.sleep(random.randint(4, 8))
    result += f"成功签到数{success_count}/{acc_num}\n签到成功率{success_count / acc_num * 100}%"
    
    hander = "云原神手动签到结果\n"
    return hander,result
    


def get_header(uuid: str, token: str):
    headers = {
        'x-rpc-combo_token':  token,
        'x-rpc-client_type':  '2',
        # 'x-rpc-app_version':  '2.4.0',
        'x-rpc-app_version':  '4.4.0',
        'x-rpc-sys_version':  '12',
        'x-rpc-channel':      'mihoyo',
        'x-rpc-device_id':    uuid,
        'x-rpc-device_name':  'Meizu 18',
        'x-rpc-device_model': 'M18',
        'x-rpc-app_id':       '1953439974',
        'Referer':            'https://app.mihoyo.com',
        'Host':               'api-cloudgame.mihoyo.com',
        'Connection':         'Keep-Alive',
        'Accept-Encoding':    'gzip',
        'User-Agent':         'okhttp/4.10.0'
    }
    return headers



async def check_token(drive_id: str, token: str):
    headers = get_header(drive_id, token)
    req = await aiorequests.post(f'{host}hk4e_cg_cn/gamer/api/login', headers=headers)

    data = req.json()
    return data['retcode'] == 0 and data['message'] == 'OK'

async def get_Announcement(uuid: str, cookie: str):
    headers = get_header(uuid, cookie)
    req = await aiorequests.get(f'{host}hk4e_cg_cn/gamer/api/getAnnouncementInfo', headers=headers)

    return req.json()

async def get_Notification(uuid: str, cookie: str):
    headers = get_header(uuid, cookie)
    req = await aiorequests.get(
        host + 'hk4e_cg_cn/gamer/api/listNotifications?status=NotificationStatusUnread&type=NotificationTypePopup'
               '&is_sort=true',
        headers=headers)
    return req.json()


async def get_Info(drive_id: str, token: str):
    '''获取一些基础信息'''
    headers = get_header(drive_id, token)
    req = await aiorequests.get(f'{host}hk4e_cg_cn/wallet/wallet/get', headers=headers)

    return req.json()


async def get_cloud_genshin_info(drive_uid: str, token: str):
    '''给定生成的随机设备ID和Token获取云原神信息'''
    
    # if not (info := await CloudGenshinSub.get_or_none(user_id=user_id, uid=uid)):
        # return f'你的UID{uid}还没有绑定云原神账户哦~请使用[云原神绑定]命令绑定账户'
    result = await get_Info(drive_uid, token)
    if result['retcode'] != 0:
        return '你的云原神token已失效，请重新绑定'
    coins = result['data']['coin']['coin_num']
    free_time = result['data']['free_time']['free_time']
    card = result['data']['play_card']['short_msg']
    # return f'======== UID: {uid} ========\n' \
    return f'剩余米云币: {coins}\n' \
           f'剩余免费时间: {free_time}分钟\n' \
           f'畅玩卡状态: {card}'
    # return coins,free_time,card
    
    
