import re
import torch
import json
import re

with open("gange","r") as f:
    gange = json.load(f)
with open("vocab","r") as f:
    vocab = json.load(f)

def generate_batch(batch):
    d = [b["ganre"] for b in batch]
    label = torch.tensor(d).to(torch.float)
    text = [torch.tensor(b["discr"]).to(torch.int64) for b in batch]

    text = torch.nn.utils.rnn.pad_sequence(text, batch_first=True)
    return text.view(-1, len(batch)), label

class Porter:
    PERFECTIVEGROUND = re.compile(u"((ив|ивши|ившись|ыв|ывши|ывшись)|((?<=[ая])(в|вши|вшись)))$")
    REFLEXIVE = re.compile(u"(с[яь])$")
    ADJECTIVE = re.compile(u"(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|ую|юю|ая|яя|ою|ею)$")
    PARTICIPLE = re.compile(u"((ивш|ывш|ующ)|((?<=[ая])(ем|нн|вш|ющ|щ)))$")
    VERB = re.compile(
        u"((ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю)|((?<=[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|нно)))$")
    NOUN = re.compile(
        u"(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$")
    RVRE = re.compile(u"^(.*?[аеиоуыэюя])(.*)$")
    DERIVATIONAL = re.compile(u".*[^аеиоуыэюя]+[аеиоуыэюя].*ость?$")
    DER = re.compile(u"ость?$")
    SUPERLATIVE = re.compile(u"(ейше|ейш)$")
    I = re.compile(u"и$")
    P = re.compile(u"ь$")
    NN = re.compile(u"нн$")

    def stem(word):
        word = word.lower()
        word = word.replace(u'ё', u'е')
        m = re.match(Porter.RVRE, word)
        if m.groups():
            pre = m.group(1)
            rv = m.group(2)
            temp = Porter.PERFECTIVEGROUND.sub('', rv, 1)
            if temp == rv:
                rv = Porter.REFLEXIVE.sub('', rv, 1)
                temp = Porter.ADJECTIVE.sub('', rv, 1)
                if temp != rv:
                    rv = temp
                    rv = Porter.PARTICIPLE.sub('', rv, 1)
                else:
                    temp = Porter.VERB.sub('', rv, 1)
                    if temp == rv:
                        rv = Porter.NOUN.sub('', rv, 1)
                    else:
                        rv = temp
            else:
                rv = temp

            rv = Porter.I.sub('', rv, 1)

            if re.match(Porter.DERIVATIONAL, rv):
                rv = Porter.DER.sub('', rv, 1)

            temp = Porter.P.sub('', rv, 1)
            if temp == rv:
                rv = Porter.SUPERLATIVE.sub('', rv, 1)
                rv = Porter.NN.sub(u'н', rv, 1)
            else:
                rv = temp
            word = pre + rv
        return word

    stem = staticmethod(stem)


def text_preproc(text):
    reg = re.compile('[^а-яА-Я ]')
    text = (reg.sub('', text))
    text = re.compile("\s+").sub(" ", text).lower()

    res = []
    for w in text.split(" "):
        try:
            if len(w) > 4:
                try:
                    res.append(vocab[Porter.stem(w)])
                except:
                    pass
            else:
                res.append(vocab[w])
        except:
            pass

    return res



class Porter:
    PERFECTIVEGROUND = re.compile(u"((ив|ивши|ившись|ыв|ывши|ывшись)|((?<=[ая])(в|вши|вшись)))$")
    REFLEXIVE = re.compile(u"(с[яь])$")
    ADJECTIVE = re.compile(u"(ее|ие|ые|ое|ими|ыми|ей|ий|ый|ой|ем|им|ым|ом|его|ого|ему|ому|их|ых|ую|юю|ая|яя|ою|ею)$")
    PARTICIPLE = re.compile(u"((ивш|ывш|ующ)|((?<=[ая])(ем|нн|вш|ющ|щ)))$")
    VERB = re.compile(
        u"((ила|ыла|ена|ейте|уйте|ите|или|ыли|ей|уй|ил|ыл|им|ым|ен|ило|ыло|ено|ят|ует|уют|ит|ыт|ены|ить|ыть|ишь|ую|ю)|((?<=[ая])(ла|на|ете|йте|ли|й|л|ем|н|ло|но|ет|ют|ны|ть|ешь|нно)))$")
    NOUN = re.compile(
        u"(а|ев|ов|ие|ье|е|иями|ями|ами|еи|ии|и|ией|ей|ой|ий|й|иям|ям|ием|ем|ам|ом|о|у|ах|иях|ях|ы|ь|ию|ью|ю|ия|ья|я)$")
    RVRE = re.compile(u"^(.*?[аеиоуыэюя])(.*)$")
    DERIVATIONAL = re.compile(u".*[^аеиоуыэюя]+[аеиоуыэюя].*ость?$")
    DER = re.compile(u"ость?$")
    SUPERLATIVE = re.compile(u"(ейше|ейш)$")
    I = re.compile(u"и$")
    P = re.compile(u"ь$")
    NN = re.compile(u"нн$")

    def stem(word):
        word = word.lower()
        word = word.replace(u'ё', u'е')
        m = re.match(Porter.RVRE, word)
        if m.groups():
            pre = m.group(1)
            rv = m.group(2)
            temp = Porter.PERFECTIVEGROUND.sub('', rv, 1)
            if temp == rv:
                rv = Porter.REFLEXIVE.sub('', rv, 1)
                temp = Porter.ADJECTIVE.sub('', rv, 1)
                if temp != rv:
                    rv = temp
                    rv = Porter.PARTICIPLE.sub('', rv, 1)
                else:
                    temp = Porter.VERB.sub('', rv, 1)
                    if temp == rv:
                        rv = Porter.NOUN.sub('', rv, 1)
                    else:
                        rv = temp
            else:
                rv = temp

            rv = Porter.I.sub('', rv, 1)

            if re.match(Porter.DERIVATIONAL, rv):
                rv = Porter.DER.sub('', rv, 1)

            temp = Porter.P.sub('', rv, 1)
            if temp == rv:
                rv = Porter.SUPERLATIVE.sub('', rv, 1)
                rv = Porter.NN.sub(u'н', rv, 1)
            else:
                rv = temp
            word = pre + rv
        return word

    stem = staticmethod(stem)


def text_preproc(text):
    reg = re.compile('[^а-яА-Я ]')
    text = (reg.sub('', text))
    text = re.compile("\s+").sub(" ", text).lower()

    res = []
    for w in text.split(" "):
        try:
            if len(w) > 4:
                try:
                    res.append(vocab[Porter.stem(w)])
                except:
                    pass
            else:
                res.append(vocab[w])
        except:
            pass

    return res

def predict(text):
    text, _ = generate_batch([{
        "discr": text_preproc(text),
        "ganre": [0]
    }])
    return text



def predict(text):
    text, _ = generate_batch([{
        "discr": text_preproc(text),
        "ganre": [0]
    }])
    return text


