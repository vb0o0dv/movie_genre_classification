# -*- coding: utf-8 -*-
"""movie_genre_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jjtkxcz4gYuD0zus-2rHo0IFPFaczyj6
    !pip install konlpy
"""



import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import pickle

pd.set_option('display.unicode.east_asian_width', True)
df = pd.read_csv('./datasets/movies_data_fin.csv',encoding='cp949')
#print(df.head())
df.info()
#print(df[df['Description'].isnull()].index.to_list())
df.drop(df[df['Description'].isnull()].index.to_list(),inplace=True)
df.reset_index(drop=True,inplace=True)



import re
X = df['Description']
Y = df['Genre']

encoder = LabelEncoder()
labeled_y = encoder.fit_transform(Y)
#print(labeled_y[:3])
label = encoder.classes_
#print(label)
with open('./encoder.pickle','wb') as f:
    pickle.dump(encoder, f)

onehot_y = to_categorical(labeled_y)
#print(onehot_y)
for i in range(len(X)):
  X[i] = re.compile('[^가-힣]').sub(' ',X[i])

okt = Okt()
for i in range(len(X)):
    X[i] = okt.morphs(X[i],stem = True)
print(X[0])
stopwords = pd.read_csv('./stopwords.csv',index_col=0)
for j in range(len(X)):
    words = []
    for i in range(len(X[j])):
        if len(X[j][i])>1:
            if X[j][i] not in list(stopwords['stopword']):
                words.append(X[j][i])
    X[j] = ' '.join(words)

print(X[0])

token = Tokenizer()
token.fit_on_texts(X)
tokened_x = token.texts_to_sequences(X)
wordsize = len(token.word_index) +1
print(tokened_x[0])
print('wordsize : ',wordsize)
with open('./movies_token.pickle','wb') as f:
    pickle.dump(token, f)

max = 0
for i in range(len(tokened_x)):
    if max < len(tokened_x[i]):
        max = len(tokened_x[i])
print('max :',max)


x_pad = pad_sequences(tokened_x, max)
print(x_pad[:3])
X_train, X_test, Y_train, Y_test = train_test_split(x_pad,onehot_y,test_size=0.2)

print(X_train.shape,Y_train.shape)
print(X_test.shape,Y_test.shape)

import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import *
from tensorflow.keras.layers import *


print(X_train.shape, Y_train.shape)
print(X_test.shape,Y_test.shape)

model = Sequential()
model.add(Embedding(30466,300,input_length=615))
model.add(Conv1D(32,kernel_size=5, padding='same',activation='relu'))
model.add(MaxPooling1D(pool_size=1))
model.add(LSTM(128, activation='tanh',return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh',return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh'))
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(128,activation='relu'))
model.add(Dense(6,activation='softmax'))
model.summary()

model.compile(loss='categorical_crossentropy',optimizer='adam',metrics = ['accuracy'])
fit_hist = model.fit(X_train,Y_train,batch_size=32,epochs=5,validation_data=(X_test,Y_test))
model.save('./movies_genre_classification_model_{}.h5'.format(fit_hist.history['val_accuracy'][-1]))
plt.plot(fit_hist.history['val_accuracy'], label = 'validation accuracy')
plt.plot(fit_hist.history['accuracy'], label = 'accuracy')
plt.legend()
plt.show()

from keras.models import load_model
from konlpy.tag import Okt
from keras.preprocessing.sequence import pad_sequences
import re
from keras.preprocessing.text import Tokenizer
import pickle
import numpy as np

model_path = "/content/movies_genre_classification_model_0.33178773522377014.h5"
tokenizer_path = "/content/movies_token.pickle"
label_encoder_path = "/content/encoder.pickle"

model = load_model(model_path)

with open(tokenizer_path, 'rb') as f:
    tokenizer = pickle.load(f)

with open(label_encoder_path, 'rb') as f:
    label_encoder = pickle.load(f)

def preprocess_sentence(sentence):
    okt = Okt()
    sentence = re.compile('[^가-힣]').sub(' ',sentence)
    tokens = okt.morphs(sentence, stem=True)
    return tokens

new_sentence = ['아라비아의 아그라바 도시에서, 알라딘은 궁전에서 나온 자스민 공주를 만나게 된다. 알라딘은 불가사의한 동굴에서 요술 램프를 찾게 되며, 램프의 지니로부터 소원을 세 번 들어주게 된다. 그러나 악한 자파의 음모로 인해 위험에 처하게 되는데..',
                '독기로 오염된 대지, 식인종과 괴물들이 활보하는 세상. 안전지대에서만 사회를 유지할 수 있는 대충 망해버린 판타지 세계.그 세계에서 꿈과 희망을 찾아 모험하는 기사 아르센의 이야기.',
                '대화산파 13대 제자, 천하십대검수 매화검존 청명. 천하를 혼란에 빠뜨린 고금제일 천마의 목을 치고 십만대산의 정상에서 영면. 백년의 시간이 지난 후 어린아이의 몸으로 다시 살아나다.',
                '발매한지 3년된 중견급 MMORPG 레전더리 에이지.[6] 작중 약칭은 LA. 마에가사키 고교 1학년생 니시무라 히데키는 레전더리 에이지의 아머 나이트(탱커) 루시안 유저인 오타쿠 남학생. 니시무라는 혼자 활동하던 솔로 플레이어였지만 1년전 길드 앨리 캣츠(길고양이들)에 들어가게 된다. 앨리 캣츠의 길드원은 마스터인 마법사 애플리코트, 소드댄서 슈바인, 힐러 아코. 루시안은 게임에서 뉴비 때 우연히 만나 그를 따라다닌 힐러 아코라는 캐릭터와 1년간 함께 길드 플레이를 하다가 아코의 적극적인 대시로 게임내 결혼을 하게 된다.그런데 아코가 길드원에게 결혼 이야기를 하던 도중 루시안의 흑역사에 대해 말하게 되면서 현실에 대한 잡담까지 확대되고, 현실 이야기를 하게 되면서 길드장 애플리코트가 즉석에서 개최를 결정한 길드 오프라인 정모에 참석하게 된다. 거기서 만나게 된 결혼 상대 아코와 길드원 애플리코트, 슈바인의 정체는 다름 아닌…',
                '도쿄 서부에 위치한 거대한 「학원도시」.총 인구는 230만 명에 달하며 그 80% 정도를 학생이 차지하는 이 도시에서는 초능력 개발을 위한 특수 교육 과정이 실시되며 학생들의 능력은 「무능력」에서 「초능력」까지 여섯 단계로 평가되고 있었다. 어떤 고등학생 카미조 토우마도 학원도시에 사는 학생 중 한 명. 그는 자신의 오른손에 깃든 힘, 이능의 힘이라면 신의 가호마저 지워버리는 「환상살」로 인해 낙제 직전의 「무능력」의 평가를 받아 불행 전속력으로 인생을 보내고 있었다. 그런 카미조의 학생 생활은 여름방학이 시작되자마자 하늘에서 내려온 순백의 수녀에 따라 크게 바뀌어버린다. 「마술」의 세계에서 도망쳐왔다는 그녀, 「금서목록」과의 만남을 기점으로, 다양한 사건에서 말려 들어가는 카미조. 학원도시가 총괄하는 「과학」 사이드. 인덱스로 이어지는 「마술」 사이드. 쌍방의 사건을 줄타기를 하듯 해결해나가다 보면, 조금씩 인맥의 범위를 넓혀나가게 된다. 그리고 마침내 마술 사이드, 십자교 최대 교단인 로마 정교가 카미조의 존재에 눈을 돌리게 된다. 마술 사이드에 호응하듯이, 과학 사이드의 학원도시도 움직인다. 그러나 갑자기 대립을 보이기 시작한 세계의 움직임에 대항하며 일어선 자들이 있었다. 카미조와 관계된 것으로, 크게 운명을 바꾼 「영웅」들. 그들 또한 몸을 내던져 세계와 대치한다. 카미조 토우마가 그렇게 해왔던 것처럼. 과학과 마술이 세 번 만나는 때, 이야기는 크게 움직이기 시작한다!',
                '최악의 로봇 센티넬과 미래에 있을 전쟁을 막기 위해, 프로페서 X와 매그니토는 울버린을 과거로 보낸다. 울버린은 흩어져 살고 있던 엑스맨들을 불러 모아 인류의 미래를 지키기 위한 치열한 전쟁을 시작한다.',
                '앤디 듀프레인은 무죄임에도 불구하고 아내와 그의 정부를 살해한 혐의로 쇼생크 교도소에 수감되며, 그곳에서 엘리스 레드딩과 친구가 됩니다. 앤디는 이후 교도소의 부패한 체제를 알게 되고, 교도소의 금융 문제를 해결해 주면서 교도소장과 간수들의 신뢰를 얻습니다. 그러나 앤디는 자신의 무죄를 증명하기 위해 끊임없이 노력하며, 결국 환상적인 계획으로 교도소에서 탈출합니다.',
                '6살의 지능을 가진 지적장애인 용구는 청소부로 일하며 어른스러운 딸 예승이와 함께 행복하게 살고 있다. 어느 날 용구는 어린 여자아이를 구하려다가 아동성범죄자로 몰린다. 담당 경찰은 사실을 교묘히 꾸미고 용구가 사형을 구형받게 한다. 그리고 용구는 곧 최고의 흉악범들이 모인 교도소 7번 방에 들어가게 된다.',
                '1950년대 한국전쟁부터 오늘날이 되기까지, 아버지 덕수는 괜찮다는 말만하며 자신보다는 가족의 행복을 위해 살아왔다. 독일 광산에도 가고, 베트남 전쟁에도 참전했던 그의 다채롭고 가슴 뭉클한 이야기가 시작된다.',
                '세무 변호사 송우석은 집도 가난하고, 배운 것도 없고, 인맥도 없지만, 탁월한 사업 능력으로 승승장구한다. 그리고 대기업의 스카우트 제의까지 받으면서 승진을 앞에 두고 있는데, 7년 전 우연히 만나 우정을 쌓아오던 국밥집 아들 진우가 재판을 받는다는 소식을 듣는다. 구치소에 면회하러 간 우석은 고문을 당한 진우를 보고 정부를 상대로 한 소송에서 진우의 변호를 맡는다.',
                '엄청난 괴력을 자랑하는 형사 마석도와 반장 전일만은 도시를 휘어잡은 신흥범죄조직의 보스 장첸을 비롯한 도시의 범죄조직을 일망타진할 작전을 세우기 시작한다. 형사들과 주민들의 합동작전과 더불어 마석도와 장첸의 일대일 격돌이 펼쳐진다.',
                '친척집에서 구박받는 생활을 하던 해리는 11살 생일을 앞두고 호그와트 마법학교로부터 입학초대장을 받고 자신이 마법사라는 사실을 알게 된다. 해리는 호그와트 마법학교로 가는 열차에서 친구 론과 헤르미온느를 사귀고 함께 마법과 신비, 모험으로 가득한 학교생활을 시작한다.'
]

# maxlen 값이 정의되어 있지 않아서 임의의 값을 50으로 설정했습니다. 필요한 경우 값을 수정해주세요.
max_length = 615

for i in enumerate(new_sentence):
  tokenized_sentence = preprocess_sentence(i)
  sequences = tokenizer.texts_to_sequences([tokenized_sentence])
  padded_sequences = pad_sequences(sequences, maxlen=max_length)

  # 예측 수행
  predictions = model.predict(padded_sequences)
  predicted_genre = label_encoder.classes_[np.argmax(predictions)]

  top_2_indices = predictions[0].argsort()[-2:][::-1]
  top_2_genres = label_encoder.classes_[top_2_indices]

  print(f"1번째 예측된 장르: {top_2_genres[0]}, 2번째 예측된 장르: {top_2_genres[1]}")
