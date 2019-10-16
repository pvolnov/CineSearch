import json
import sys

import pandas as pd
import sklearn
import xgboost as xgb
sys.path.append('../')
sys.path.append('./')
import numpy as np
from playhouse.shortcuts import model_to_dict

from models import Users, Films


def get_group(user):
    from sklearn.cluster import AffinityPropagation
    import numpy as np
    import pickle
    with open('clustering', 'rb') as f:
        clustering = pickle.load(f)

    ujson = model_to_dict(user)
    ujson["last_visit"] = ""

    user = user_preparation(ujson)
    df_user = pd.DataFrame.from_dict([user]).fillna(0)
    df_user=df_user.reindex(sorted(df_user.columns), axis=1)

    return clustering.predict(df_user)[0]

def update_all_group(user):
    from sklearn.cluster import AffinityPropagation
    # import numpy as np
    # clustering = AffinityPropagation().fit(df_train)
    #
    # AffinityPropagation(affinity='euclidean', convergence_iter=15, copy=True,
    #                     damping=0.5, max_iter=200, preference=None, verbose=False)
    #
    # clustering.predict(df_train[0:1])
    #
    # import pickle
    # with open('clustering', 'wb') as f:
    #     pickle.dump(clustering,f)
    #
    # for u in Users.select().execute():
    #     u.group = get_group(u)
    #     u.save()



def vcos(a, b):
    ch = 0
    znA = 0
    znB = 0
    for c in zip(a, b):
        ch += c[0] * c[1]
        znA += c[0] * c[0]
        znB += c[1] * c[1]
    if ch == 0:
        return 1
    return ch / ((znA ** 0.5) * (znB ** 0.5))


def feature_selection(df_train):
    df_train["year"] = 2019 - df_train["year"]
    df_train["dage"] = df_train["meanage"] - df_train["age"]
    df_train["dsex"] = df_train["usex"] - df_train["sex"]

    df_train["quality"] = df_train["likes"] / (df_train["dislikes"] + df_train["likes"] + df_train["shit"] * 2)
    df_train["result"] = (df_train["result"] > 0).astype(np.float32)
    return df_train


def user_preparation(data):
    del data["nicname"]
    del data["predict_films"]
    del data["id"]
    del data["cfmes"]
    del data["ustatus"]
    del data["tel_id"]
    del data["ctmes"]
    del data["last_visit"]
    del data["cfid"]
    del data["cms"]
    del data["info"]
    del data["vk_id"]
    del data["group"]

    data["popular"] = len(data["selections"])
    del data["selections"]

    msex = 0
    mage = 0
    myers = 0
    liked_films = Films.select().where(Films.film_id.in_(data["liked"] + data["viewed"])).execute()
    for f in liked_films:
        msex += f.sex
        mage += f.meanage
        myers += 2019 - f.year

    data["myers"] = myers / (len(liked_films) + 1)
    data["mage"] = mage / (len(liked_films) + 1)
    data["msex"] = msex / (len(liked_films) + 1)

    g2 = data["ganres"]
    for i in range(24):
        if str(i) not in g2:
            g2[str(i)] = 0
        data["UserGanre_" + str(i)] = g2[str(i)]

    g2 = [t[1] for t in sorted(g2.items(), key=lambda kv: int(kv[0]))]

    del data["ganres"]
    if not "just_marked" in data:
        data["just_marked"] = len(data["viewed"]) + len(data["liked"]) + len(data["disliked"])

    if not "mark_wight" in data:
        data["mark_wight"] = (len(data["viewed"]) * 2 + len(data["liked"]) + len(data["disliked"]) * -1.3) / data[
            "just_marked"]

    del data["viewed"]
    del data["disliked"]
    del data["liked"]

    #         print(data["name"]+": ",data)
    del data["name"]

    return data

def preparation(data):
    data = {"uganres": data["user_value"]["ganres"], "uselections": data["user_value"]["selections"],
            "usex": data["user_value"]["sex"],
            **data["user_value"], **data["film_value"], "result": data["result"]}
    del data["nicname"]
    del data["youtube"]
    del data["discr"]
    del data["img"]
    del data["info"]
    del data["predict_films"]
    del data["id"]
    del data["cfmes"]
    del data["ustatus"]
    del data["tel_id"]
    del data["ctmes"]
    del data["last_visit"]
    del data["cfid"]
    del data["cms"]
    del data["film_id"]
    del data["level"]
    del data["group"]


    ssum = 0
    count = 1

    for s in data["uselections"]:
        if int(s) in data["selections"]:
            try:
                ssum += data["uselections"][s] + 1 - data["result"] * 2
                count += 1
            except:
                ssum += 1.2
                count += 1
    #                     print("error")

    data["mean_similar"] = (ssum / count) if ssum > 0 else 0
    del data["uselections"]
    data["popular"] = len(data["selections"])
    del data["selections"]

    gsum = 0
    g1 = {}
    for g in data["ganres"]:
        g1[str(g)] = 1
        if str(g) in data["uganres"]:
            gsum += data["uganres"][str(g)]

    g2 = data["uganres"]
    for i in range(24):
        if str(i) not in g1:
            g1[str(i)] = 0
        if str(i) not in g2:
            g2[str(i)] = 0
        data["UserGanre_" + str(i)] = g2[str(i)]
        data["FilmGanre_" + str(i)] = g1[str(i)]

    g1 = [t[1] for t in sorted(g1.items(), key=lambda kv: int(kv[0]))]
    g2 = [t[1] for t in sorted(g2.items(), key=lambda kv: int(kv[0]))]

    dcos = vcos(g1, g2)
    data["ganre_delta"] = dcos
    data["ganre_total"] = (gsum / sum(g2)) if sum(g2) > 0 else 0

    del data["uganres"]
    del data["ganres"]
    if not "just_marked" in data:
        data["just_marked"] = len(data["viewed"]) + len(data["liked"]) + len(data["disliked"])

    if not "mark_wight" in data:
        data["mark_wight"] = (len(data["viewed"]) * 2 + len(data["liked"]) + len(data["disliked"]) * -1.3) / data[
            "just_marked"]

    if not "shit" in data:
        data["shit"] = 0
    if not "opening" in data:
        data["opening"] = 0

    if data["stars"] > 10:
        data["stars"] = (data["likes"] * 10 + data["dislikes"] * 3 + data["shit"] +7) / (
                data["likes"] + data["dislikes"] + data["shit"] +1 )

    data["year"]

    del data["viewed"]
    del data["disliked"]
    del data["liked"]

    #         print(data["name"]+": ",data)
    del data["name"]

    return data


def get_predict(datalist, n=20):
    dataset = []
    for data in datalist:
        data = preparation(data)
        dataset.append(data)

    df = pd.DataFrame.from_dict(dataset).fillna(0)
    df = feature_selection(df)
    df = df.reindex(sorted(df.columns), axis=1)

    df.drop(['vk_id', 'result'], inplace=True, axis=1)

    import pickle
    with open('gbm', 'rb') as f:
        gbm = pickle.load(f)

    predictions = gbm.predict_proba(df)[:, 1]
    # print(predictions)

    pred = {}
    for i in range(len(df)):
        pred[i] = predictions[i] - (df.loc[i]["year"]) / 100
    print(pred.values())

    return sorted(pred, key=lambda k: pred[k])[-20:]


def predict_alg(u, options, CONFIG):
    predict = {}
    sel_sum = sum(u.selections.values()) + 1  # mean selection priority
    ganr_sum = sum(u.ganres.values()) + 1  # mean selection priority

    selections = {s: u.selections[s] / sel_sum for s in u.selections}
    ganres = {g: u.ganres[g] / ganr_sum for g in u.ganres}

    for o in options:  # all avilible films
        predict[o.film_id] = 1
        scount = 0
        for s in o.selections:  # all users fun categories
            if s in selections:  # film is in user`s fun group
                scount += selections[s]  # how important is this group

        gcount = 0
        for g in o.ganres:
            if g in ganres:
                gcount += u.ganres[g]

        g1 = {}
        for g in o.ganres:
            g1[str(g)] = 1

        g2 = u.ganres
        for i in range(25):
            if str(i) not in g1:
                g1[str(i)] = 0
            if str(i) not in g2:
                g2[str(i)] = 0

        g1 = [t[1] for t in sorted(g1.items(), key=lambda kv: int(kv[0]))]
        g2 = [t[1] for t in sorted(g2.items(), key=lambda kv: int(kv[0]))]

        dcos = vcos(g1, g2)

        predict[o.film_id] += dcos * int(CONFIG["WEIGHT_COS"])
        predict[o.film_id] += gcount * int(CONFIG["WEIGHT_GANRE"])  # доля жанров фильма в наших фаворитах
        predict[o.film_id] += scount * int(CONFIG["WEIGHT_SELECTION"])  # доля любимых коллеекций среди фильмов
        predict[o.film_id] += o.stars * int(CONFIG["WEIGHT_STARS"])
        predict[o.film_id] += 1 / (abs(o.meanage - u.age) + 1) * int(CONFIG["WEIGHT_AGE"])
        predict[o.film_id] += 1 / (abs(o.sex - u.sex) * 10 + 1) * int(CONFIG["WEIGHT_SEX"])
        predict[o.film_id] += (o.likes) / (o.likes + o.dislikes + 1) * int(CONFIG["WEIGHT_LIKE"])
        predict[o.film_id] += (1 / (2020 - o.year)) * int(CONFIG["WEIGHT_YEAR"])
        predict[o.film_id] -= o.shit * int(CONFIG["WEIGHT_YEAR"])
        if o.year < 2000:
            predict[o.film_id] -= 4

    pb = np.array(list(predict.values()), dtype='float')
    pb /= pb.sum()
    try:
        predict = [int(p) for p in list(predict.keys())]
        pred = np.random.choice(predict, p=pb, size=20)
    except Exception as e:
        pred = predict[-20:]

    return list(set([p.item() for p in pred]))
