'''
笨比ZiHao移植的独立版云原神签到
写的比较屎qwq 我尽量不写抽象（
主打就是一个能跑就行

原作者
https://github.com/CMHopeSunshine/LittlePaimon

'''

import re
import uuid

from nonebot import on_command
# from nonebot.params import CommandArg
# from nonebot.typing import T_State

from nonebot.adapters.telegram.bot import Bot
from nonebot.adapters.telegram.event import MessageEvent
from nonebot.adapters.telegram.message import Reply,Entity


from .database import *
from .api import get_cloud_genshin_info,get_hand_qd


yys_bind = on_command('yys_bind')

yys_info = on_command('yys_info')

yys_delete = on_command('yys_delete')

'''遗憾的是..TG的机器人命令只支持英文'''

yys_qd = on_command("yys_qd")

uuid_ = str(uuid.uuid4())

BotName = "@YourBotName"


    
@yys_bind.handle()
async def _(event: MessageEvent,bot:Bot):
    # msg = msg.extract_plain_text().strip()
    msg = event.message.extract_plain_text().replace("/yys_bind","").replace(BotName,"").strip()
    chatid = event.chat.id
    msgid_main = event.message_id

    if not msg:
        
        
        await bot.send(event,"请在命令后给出要绑定的token" + Reply.reply(msgid_main,chatid))

        await yys_bind.finish()
    if match := re.search(r'oi=\d+', msg):
        # group_id = event.group_id if isinstance(event, GroupMessageEvent) else event.user_id
        uid = str(match.group()).split('=')[1]
        # await CloudGenshinSub.update_or_create(user_id=str(event.user_id), uid=uid, defaults={'group_id': group_id, 'uuid': uuid_, 'token': msg})
        Save_or_Update(user_id=event.get_user_id(),give_uid=uid,drive_uid=uuid_,token=msg)
        
        fdb_msg = Entity.text(f'米游社账号') + Entity.code(uid) + Entity.text("云原神token绑定成功\n将会每日为你自动领免费时长")
        
        await bot.send(event,fdb_msg + Reply.reply(msgid_main,chatid))
        
        await bot.delete_message(chatid,message_id=event.message_id)
        #删除用户发送的token消息
        await yys_bind.finish()
    else:
        await bot.send(event,'token格式错误哦~\n请自行寻找相关教程后重试' + Reply.reply(msgid_main,chatid))
        # 原链接好像似了 打不开
        # https://blog.ethreal.cn/archives/yysgettoken所写的方法获取
        await yys_bind.finish()

@yys_info.handle()
async def _(event: MessageEvent,bot:Bot):
    msg = event.message.extract_plain_text().replace("/yys_info","").replace(BotName,"").strip()

    chatid = event.chat.id
    msgid_main = event.message_id
    user_id=event.get_user_id()
    if not msg:
            
        msg_mix = From_userid_get_msg(user_id)
        
        msg_mixp2 = msg_mix.replace("你已绑定的云原神账号有\n","")
        msg_fmix = Entity.text("你已绑定的云原神账号有\n") + Entity.code(msg_mixp2)
        
        await bot.send(event,msg_fmix + Reply.reply(msgid_main,chatid))
        await yys_info.finish()
    else:
        msg_mix = From_userid_get_msg(user_id)
        if msg_mix =="你还没有绑定云原神账号哦~\n请使用云原神绑定指令绑定账号":
            
            # fdb_msg = f'你的UID{msg}还没有绑定云原神账户哦~请使用/云原神绑定[token]命令绑定账户'
            fdb_msg = Entity.text("你的UID") + Entity.code(msg) + Entity.text("还没有绑定云原神账户哦~\n请使用") + Entity.code("/云原神绑定[token]") + Entity.text("命令绑定账户")
            await bot.send(event,fdb_msg + Reply.reply(msgid_main,chatid))
            await yys_info.finish()
            
        else:
            
            did,tokeng = From_userid_get_did_token(user_id,msg)
            
            fdb = await get_cloud_genshin_info(did,tokeng)
            
            if fdb =="你的云原神token已失效，请重新绑定":
                From_userid_del_data(user_id,msg)
            
            await bot.send(event,Entity.code(fdb)+ Reply.reply(msgid_main,chatid))
            await yys_info.finish()
    


@yys_delete.handle()
async def _(event: MessageEvent,bot:Bot):
    msg = event.message.extract_plain_text().replace("/yys_delete","").replace(BotName,"").strip()

    chatid = event.chat.id
    msgid_main = event.message_id
    user_id=event.get_user_id()    
    if not msg:
        await bot.send(event,f"你是要解除绑定嘛?\n发送/云原神解绑 [uid]解绑单独的账号\n发送/云原神解绑 全部 来解绑*全部账号*" + Reply.reply(msgid_main,chatid))
        
        res = From_userid_get_msg(user_id)
        if res =="不过...你还没有绑定云原神账号哦~\n请使用/云原神绑定[token]指令绑定账号":
            await bot.send(event,res + Reply.reply(msgid_main,chatid))
            await yys_info.finish()
            
        else:
            remove_titile = res.replace("你已绑定的云原神账号有\n","")
            await bot.send(event,Entity.text("你已绑定的云原神账号有\n") + Entity.code(remove_titile))
            await yys_info.finish()
    
    if '全部' in msg:
        
        res = From_userid_get_msg(user_id)
        if res =="你还没有绑定云原神账号哦~\n请使用/云原神绑定[token]指令绑定账号":
            await bot.send(event,res + Reply.reply(msgid_main,chatid))
            await yys_info.finish()
        else:
            From_userid_del_data(user_id,given_uid=None)
            await bot.send(event,f"芜~~已解除你全部云原神账号绑定了" + Reply.reply(msgid_main,chatid))
            await yys_info.finish()
    else:
        res = From_userid_get_msg(user_id)
        if res =="你还没有绑定云原神账号哦~\n请使用/云原神绑定[token]指令绑定账号":
            await bot.send(event,res + Reply.reply(msgid_main,chatid))
            await yys_info.finish()
        else:
            From_userid_del_data(user_id,given_uid=msg)
            await bot.send(event,f"解除云原神账号{msg}绑定成功" + Reply.reply(msgid_main,chatid))
            await yys_info.finish()

@yys_qd.handle()
async def _(bot:Bot,event:MessageEvent):
    chatid = event.chat.id
    msgid_main = event.message_id
    user_id=event.get_user_id()
    st = await bot.send(event,"开始进行云原神手动签到\n请稍安勿躁...")
    await bot.send_chat_action(chatid,action="typing")
    
    res = From_userid_get_msg(user_id)
    if res =="你还没有绑定云原神账号哦~\n请使用/云原神绑定[token]指令绑定账号":
        await bot.send(event,res + Reply.reply(msgid_main,chatid))
        await bot.delete_message(chatid,message_id=st.message_id)
        await yys_qd.finish()
    else:
        uids,dids,toks = From_userid_get_userdata(user_id)
        hand,result = await get_hand_qd(user_id,uids,dids,toks)
        mixs = Entity.text(hand) + Entity.code(result)
        await bot.send(event,mixs+Reply.reply(msgid_main,chatid))
            
    