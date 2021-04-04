import sqlite3
import os
import json
import datetime


def calculate_reputation(user_id: int):
    captcha_fails, mutes, reports, kicks, bans = check_user_flags(user_id)
    points = mutes * 2 + reports + kicks * 2 + bans * 2
    return points


def add_report(user_id: int, reporter_id: int, reason: str):
    try:
        try:
            os.mkdir("reports/" + str(user_id))
        except:
            pass
        now = datetime.datetime.now().strftime("--%Y-%m-%d_%H_%M_%S")
        report_user_path = "reports/" + str(user_id) + now + ".json"
        report = dict(
            reporter_id=reporter_id,
            reason=reason
        )
        with open(report_user_path, 'w') as f:
            json.dump(report, f)
        return True
    except Exception as e:
        print(e)
        return False


def check_guild_setup(guild_id: int):
    path_settings = "guild/" + str(guild_id) + "/core_settings.json"
    if os.path.isfile(path_settings):
        with open(path_settings, 'r') as f:
            settings = json.load(f)
            return settings["log_channel_id"], \
                   settings["verified_role_id"], \
                   settings["captcha_level"], \
                   settings["security_activated"]
    return None, None, None, None


def check_user_flags(user_id: int):
    path_flags = "user/" + str(user_id) + "/flags.json"
    print(path_flags)
    if os.path.isfile(path_flags):
        with open(path_flags, 'r') as f:
            settings = json.load(f)
            return settings["captcha_fails"], \
                   settings["mutes"], \
                   settings["reports"], \
                   settings["kicks"], \
                   settings["bans"]
    print("returned non")
    return None, None, None, None, None


def increase_user_flag(user_id: int, captcha_fails_to_add=None, mutes_to_add=None, reports_to_add=None,
                       kicks_to_add=None, bans_to_add=None):
    captcha_fails, mutes, reports, kicks, bans = check_user_flags(user_id)
    path_flags = "user/" + str(user_id) + "/flags.json"
    if captcha_fails_to_add is not None:
        captcha_fails += captcha_fails_to_add
    if mutes_to_add is not None:
        mutes += mutes_to_add
    if reports_to_add is not None:
        reports += reports_to_add
    if kicks_to_add is not None:
        kicks += kicks_to_add
    if bans_to_add is not None:
        bans += bans_to_add

    new_flags = dict(
        captcha_fails=captcha_fails,
        mutes=mutes,
        reports=reports,
        kicks=kicks,
        bans=bans
    )

    os.remove(path_flags)
    with open(path_flags, 'w') as f:
        json.dump(new_flags, f)


def add_user(user_id: int):
    try:
        try:
            os.mkdir("user/" + str(user_id))
        except:
            pass
        path_user_flags = "user/" + str(user_id) + "/flags.json"

        if not os.path.isfile(path_user_flags):
            flags = dict(
                captcha_fails=0,
                mutes=0,
                reports=0,
                kicks=0,
                bans=0
            )
            if os.path.isfile(path_user_flags):
                pass
            else:
                with open(path_user_flags, 'w') as f:
                    json.dump(flags, f)
                return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def add_guild(guild_id: int):
    try:
        try:
            os.mkdir("guild/" + str(guild_id))
        except:
            pass
        path_settings = "guild/" + str(guild_id) + "/core_settings.json"
        settings = dict(
            log_channel_id=None,
            verified_role_id=None,
            captcha_level=None,
            security_activated=None
        )

        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(guild_id)

        if log_channel_id is None and verified_role_id is None and captcha_level is None:
            # guild setup not started
            # removing file and creating again is safe
            try:
                os.remove(path_settings)
            except:
                pass
            with open(path_settings, 'w') as f:
                json.dump(settings, f)
            return True
        else:
            # guild setup has started, cannot delete safely
            return False
    except Exception as e:
        print(e)
        return False


def set_guild_setting(guild_id: int,
                      new_log_channel_id=None,
                      new_verified_role_id=None,
                      new_captcha_level=None,
                      new_security_activated=None
                      ):
    path_settings = "guild/" + str(guild_id) + "/core_settings.json"
    if os.path.isfile(path_settings):
        with open(path_settings, 'r') as f:
            settings = json.load(f)
    log_channel_id = settings["log_channel_id"]
    verified_role_id = settings["verified_role_id"]
    captcha_level = settings["captcha_level"]
    security_activated = settings["security_activated"]

    if new_log_channel_id is not None:
        log_channel_id = new_log_channel_id
    if new_verified_role_id is not None:
        verified_role_id = new_verified_role_id
    if new_captcha_level is not None:
        captcha_level = new_captcha_level
    if new_security_activated is not None:
        security_activated = new_security_activated

    new_settings = dict(
        log_channel_id=log_channel_id,
        verified_role_id=verified_role_id,
        captcha_level=captcha_level,
        security_activated=security_activated
    )

    os.remove(path_settings)
    with open(path_settings, 'w') as f:
        json.dump(new_settings, f)
