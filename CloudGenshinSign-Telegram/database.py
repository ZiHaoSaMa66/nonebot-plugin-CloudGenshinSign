from pathlib import Path
import json
import os

from nonebot.log import logger

Save_DIR = (
Path() / "CloudGenshin"
)
Save_DIR.mkdir(parents=True, exist_ok=True)
#下载的图片

def get_path_without_filename():
    '''获取路径的字符串'''
    Str_DIR = str(Path(Save_DIR))
    fdb = Str_DIR
    return fdb

def get_path_with_filename(filename:str):
    '''获取路径的字符串 提供文件名进行MIX'''
    Str_DIR = str(Path(Save_DIR))
    fdb = Str_DIR + "/" + filename
    return fdb

def Save_or_Update(user_id,give_uid,drive_uid,token):
    '''以user_id保存基础相关数据'''
    path=get_path_with_filename(f"{str(user_id)}.json")
    try:
        with open(path, "r") as fm:
            get_data = json.load(fm)
        zhanghao_count = get_data["COUNT"]
        zhanghao_max = get_data["Max"]
        
        found = False

        # 遍历每个 "zhanghao_*" 的数据
        for key, value in get_data.items():
            if key.startswith("zhanghao_"):  
                if value.get("uid") == give_uid:
                    found = True
                    print(f"找到匹配的 uid: {give_uid}，在键为 {key} 的数据中。")
                    break

        if not found:
            print(f"未找到匹配的 uid: {give_uid}。")
            logger.info("将写入新UID数据")
            now_count = int(zhanghao_count) + 1
            
            get_data["COUNT"] = now_count
            get_data["Max"] = int(zhanghao_max) + 1
            # 一个粗暴的解决删除后可能覆盖的问题(
            
            get_data[f"zhanghao_{zhanghao_max + 1}"] = {
            "uid": give_uid,
            "token": token,
            "drive_uid": drive_uid
        }
            
            with open(path, "w") as fm:
                dunp = json.dump(get_data,fm)
                
                
        else:
            print("已有相同UID 跳过保存")
            
    except FileNotFoundError:
        logger.info(f"{user_id}为第一次绑定将使用模版数据")
        
        with open(path, "w") as fm:
            data = {
                "COUNT": 1,
                "Max": 1,
                "zhanghao_1": {
                    
                    "uid": give_uid,
                    "token":token,
                    "drive_uid": drive_uid
                }
            }
            dunp = json.dump(data,fm)



def get_all_subs_uid_did_token():
    '''获取所有保存的uid,设备id,token\n
    返回三个列表'''
    directory=get_path_without_filename()
    
    subs_uid_list = []
    subs_did_list = []
    subs_token_list = []
    
    for filenames in os.listdir(directory):
        # print(filenames)
        # logger.info("拉取全部数据",f"开始获取来自{filenames}的数据")
        print("拉取全部数据",f"开始获取来自{filenames}的数据")
        sigpath = get_path_with_filename(filenames)
    
        with open(sigpath, "r") as fm:
            get_data = json.load(fm)
        
        for key, value in get_data.items():
            if key.startswith("zhanghao_"):  
                uid_get = get_data[key]["uid"]
                drive_id_get = get_data[key]["drive_uid"]
                token_get = get_data[key]["token"]
                
                subs_uid_list.append(uid_get)
                subs_did_list.append(drive_id_get)
                subs_token_list.append(token_get)
                
                print(f"拉取此用户的uid > {uid_get} < , > {drive_id_get} < ,token...")
    logger.success("数据已全部拉取完毕")
    return subs_uid_list,subs_did_list,subs_token_list

def From_userid_get_msg(user_id):
    '''通过User_id获取Ta的uid并组合为消息'''
    '你已绑定的云原神账号有\n'
    uids = ""
    path=get_path_with_filename(f"{str(user_id)}.json")
    try:
        with open(path, "r") as fm:
            get_data = json.load(fm)
    except FileNotFoundError:
        return "你还没有绑定云原神账号哦~\n请使用云原神绑定指令绑定账号"
    # 遍历每个 "zhanghao_*" 的数据
    for key, value in get_data.items():
        if key.startswith("zhanghao_"):  
            # 检查键是否以 "zhanghao_" 开头
            uids += str(value.get("uid")) + "\n"
        
    print("uids = ",uids)
    
    if uids == "":
        return "你还没有绑定云原神账号哦~\n请使用云原神绑定指令绑定账号"
    else:
        return "你已绑定的云原神账号有\n" + uids
    
def From_userid_get_did_token(user_id,give_uid):
    '''提供userid和uid获取设备id和token'''
    path=get_path_with_filename(f"{str(user_id)}.json")

    with open(path, "r") as fm:
        get_data = json.load(fm)
    found = False

    # 遍历每个 "zhanghao_*" 的数据
    for key, value in get_data.items():
        if key.startswith("zhanghao_"):  
            if value.get("uid") == give_uid:  
                found = True
                print(f"找到匹配的 uid: {give_uid}，在键为 {key} 的数据中。")
                
                drive_id_get = get_data[key]["drive_uid"]
                token_get = get_data[key]["token"]

                break
    
    if not found:
        print("未找到对应UID的数据")
        return None,None
    
    return drive_id_get,token_get

def From_alldata_del_uid(given_uid:str):
    '''给定uid来进行UID删除'''
    logger.info(f"开始检索{given_uid}的UID进行删除")
    directory=get_path_without_filename()
    
    for filenames in os.listdir(directory):
        
        path=get_path_with_filename(f"{str(filenames)}.json")
        
        with open(path, "r") as fm:
            data = json.load(fm)
        
        if given_uid != None:
            found_key = None

            # 遍历每个 "zhanghao_*" 的数据
            for key, value in data.items():
                if key.startswith("zhanghao_"):  
                    # 检查键是否以 "zhanghao_" 开头
                    if value.get("uid") == given_uid:  
                        # 检查当前条目的 uid 是否与给定的 uid 匹配
                        found_key = key
                        break

            if found_key:
                del data[found_key]  
                data["COUNT"] -= 1  
                print(f"已删除 uid 为 {given_uid} 的数据")
                with open(path, "w") as fm:
                    dunp = json.dump(data,fm)
                break

def From_userid_get_userdata(user_id:str):
    '''给定用户id返回此用户的uid,driveid,token的列表'''
    
    debug = user_id.find(".json")
    
    subs_uid_list = []
    subs_did_list = []
    subs_token_list = []
    
    
    if debug == -1:
    
        sigpath = get_path_with_filename(f"{user_id}.json")
    
    with open(sigpath, "r") as fm:
        get_data = json.load(fm)
    

    for key, value in get_data.items():
        if key.startswith("zhanghao_"):  
            uid_get = get_data[key]["uid"]
            drive_id_get = get_data[key]["drive_uid"]
            token_get = get_data[key]["token"]

            subs_uid_list.append(uid_get)
            subs_did_list.append(drive_id_get)
            subs_token_list.append(token_get)
            
    return subs_uid_list,subs_did_list,subs_token_list

def From_userid_del_data(user_id,given_uid:str | None):
    '''给定用户id和uid来进行整个文件删除/单独UID删除 \n
        若需要整个文件删除将given_uid设置为None即可'''
    
    path=get_path_with_filename(f"{str(user_id)}.json")
    
    with open(path, "r") as fm:
        data = json.load(fm)
    
    if given_uid != None:
        found_key = None

        # 遍历每个 "zhanghao_*" 的数据
        for key, value in data.items():
            if key.startswith("zhanghao_"):  
                # 检查键是否以 "zhanghao_" 开头
                if value.get("uid") == given_uid:  
                    # 检查当前条目的 uid 是否与给定的 uid 匹配
                    found_key = key
                    break

        if found_key:
            del data[found_key]  
            # 如果找到匹配的 uid，则删除对应的键值对
            data["COUNT"] -= 1  
            # 更新 COUNT 值，减去已删除的条目

            print(f"已删除 uid 为 {given_uid} 的数据。")
            
            with open(path, "w") as fm:
                dunp = json.dump(data,fm)
            
            print("更新后的数据：")
            print(data)
            
            
            
        else:
            print(f"未找到匹配的 uid: {given_uid}，无需删除。")
    else:
        
        
        os.remove(path)