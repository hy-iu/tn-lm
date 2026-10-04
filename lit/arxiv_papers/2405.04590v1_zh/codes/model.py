import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init
import pickle
import os
import numpy as np
import random
from torch.utils.data import DataLoader
import torch.optim as optim
from tqdm import tqdm
import argparse
import pickle
import numpy as np
from torch.utils.data import Dataset

parser = argparse.ArgumentParser(description='parameter information')
parser.add_argument('--output', dest='output', default= "output" , type=str, help='output dir to save embeddings')
parser.add_argument('--log_step', dest='log_step', default= 1 , type=int, help='log_step')
parser.add_argument('--from_scatch', dest='from_scatch', default= 1 , type=int, help='from_scatch or not')
parser.add_argument('--batch_size', dest='batch_size', default= 64, type=int, help='batch_size')
parser.add_argument('--emb_dimension', dest='emb_dimension', default= 10 , type=int, help='emb_dimension')
parser.add_argument('--add_phase_shift', dest='add_phase_shift', default= 0, type=int, help='add_phase_shift')
parser.add_argument('--verbose', dest='verbose', default= 0, type=int, help='verbose')
parser.add_argument('--lr', dest='lr', default= 0.005, type=float, help='learning rate')
parser.add_argument('--lambda_rate', dest='lambda_rate', default= 0.01, type=float, help='lambda_rate')
parser.add_argument('--do_eval', dest='do_eval', default= 0, type=int, help='verbose')
parser.add_argument('--max_seq', dest='max_seq', default= 10, type=int, help='max_seq')
parser.add_argument('--weight_decay', dest='weight_decay', default= 0.01, type=float, help='weight_decay')
parser.add_argument('--iterations', dest='iterations', default= 10000, type=int, help='iterations')
parser.add_argument('--pair_pattern', dest='pair_pattern', default= 0, type=int, help='pair_pattern') # semtence pair classification or sentence classification


args = parser.parse_args()
if not  torch.cuda.is_available(): # debug in cpu
    args.verbose = 1


noun = "dog cat pig cook meal code  programmer "
adj = "good bad nice complicated skillful"
adv = "probably rudely necessarily  carefully"
verb = "beats fucks likes prepares writes"

PADDING_STR = "<pading>"

vocab = [word for pos in [noun,adj,adv,verb] for word in pos.split()] + [PADDING_STR]
vocab_size = len(vocab)

def generate_word(words = "dog cat pig"):
    words = words.split()
    index = random.randint(0,len(words)-1)
    return words[index]

# rules
# S -> NP VP
# NP -> N
# NP -> ADJ N 
# VP -> VB NP
# VP -> ADV VB NP

def S(): 
    return NP() + " " +  VP()

def NP():
    if random.random()>0.5:
        return generate_word(noun)
    else:
        return generate_word(adj) + " " +  generate_word(noun)

def VP():
    if random.random()>0.5:
        return generate_word(verb) + " " + NP()
    else:
        return generate_word(adv) + " " +  generate_word(verb) +  " " +  NP()

sents = [] 

stem_table = {"code":"programmer","cook":"meal"}

def get_sentence_pair_dataset():
    examples =["\t".join([S(), S()]) for i in range(500)]

    for s in set(examples):
        s1, s2 = s.split("\t")  
        label = 0

        stemed_s1, stemed_s2 = s1, s2
        for key,value in stem_table.items():
            stemed_s1 = stemed_s1.replace(key,value)
            stemed_s2 = stemed_s2.replace(key,value)
        for word in stem_table.values(): # fake label generation: whether two sentence talking about the same topic, either coding or programing
            if word in stemed_s1 and word in stemed_s2:
                label =1
        sents.append((s1,s2,label))
        if args.verbose:
            print("{} <sep> \t {} : {}".format(s1,s2,label))

    train_size = int(len(sents)*0.8)
    train , test = sents[:train_size],sents[train_size:]
    print("generating {} training sentence pairs".format(len(train) ))
    return train,test 


def get_sentence_dataset():
    examples = [S() for i in range(500)]
    # print(set(examples))

    for s1 in set(examples): 

        label = 0
        for word in "code  programmer".split(): # fake label generation: whether two sentence talking about the same topic, either coding or programing
            if word in s1:
                label =1
        sents.append((s1,label))
        if args.verbose:
            print("{}  \t  {}".format(s1,label))
    train_size = int(len(sents)*0.8)
    train , test = sents[:train_size],sents[train_size:]
    print("generating {} training sentence ".format(len(train) ))
    return train , test 


class TN(nn.Module):
    def __init__(self, d= 10,vocab_size=vocab_size):
        super().__init__()
        self.d = d
        self.encoder =  nn.Embedding(vocab_size, d*d)
        self.init_matrix = nn.Parameter(torch.Tensor(1,d))
        self.linear = torch.nn.Linear(d,1)
    def encoding(self,x):
        batch_size,seq_length = x.shape[0],x.shape[1]

        encoded = self.encoder(x)

        encoded = encoded.view(batch_size, seq_length,self.d,self.d)

        result = self.init_matrix.unsqueeze(0).repeat([batch_size,1,1]) 
        for i in range(seq_length):
            result = torch.bmm(result,encoded[:,i,:,:])
        return result.squeeze()

    def forward(self,x):
        encoded_x = self.encoding(x)
        return self.linear(encoded_x).squeeze()
        

    def get_structure_penalty(self): # unitary or l2 loss
        embedding = self.encoder.weight.view(-1,self.d,self.d)
        embedding_transpose = embedding.transpose(-1,-2)
        product = torch.bmm(embedding_transpose,embedding)
        diff = torch.abs(product.mean(0).squeeze() -torch.eye(self.d,device=torch.device("cuda" if torch.cuda.is_available() else "cpu")))
        return torch.sum(diff)


class Match(nn.Module):
    def __init__(self, d= 10,vocab_size=vocab_size):
        super().__init__()
        self.tn = TN(d=d, vocab_size=vocab_size)
    def forward(self,x,y):
        encode_x ,encode_y = self.tn.encoding(x),  self.tn.encoding(y)
        logist = torch.sum(torch.mul(encode_x,encode_y),dim = -1)
        # return torch.softmax(logist,-1)
        return logist
    def get_structure_penalty(self):
        return self.tn.get_structure_penalty()



class DataReader:
    def __init__(self, sents = None,vocab = None, max_seq = 128):
        self.sents = sents
        self.max_seq = max_seq
        if vocab is None and sents is not None:
            vocab = self.build_vocob(sents)
        
        self.word2id, self.id2word =  {word: index for index,word in enumerate(vocab)}, {index: word for word, index in enumerate(vocab)}
        self.pading = self.word2id[PADDING_STR]
    def build_vocob(self): # not tested yet
        vocab = set()
        sents = [ [item[0],item[1]] for item in self.sents]
        vocab.add(PADDING_STRPADDING_STR)
        for sent in sents:
            vocab.addall(sent.split())
        return vocab


class TNDataset(Dataset):
    def __init__(self, data,sents):
        self.data = data
        self.sents = sents

    def __len__(self):
        return len(self.sents)

    def encoding(self,s):
        tokens = s.split()
        return [ self.data.word2id[word]  for word in tokens][:self.data.max_seq] + [self.data.pading]*(self.data.max_seq - len(tokens))
    def __getitem__(self, idx):
        # while True:

        # s1_encoded = [self.encoding(s1) for s1, s2, label in self.sents]
        # s2_encoded = [self.encoding(s2) for s1, s2, label in self.sents]
        # labels = [label for s1, s2, label in self.sents]
        s1_encoded = self.encoding( self.sents[idx][0] )
        if len(self.sents[idx]) ==3:
            s2_encoded = self.encoding( self.sents[idx][1] )
            label =  self.sents[idx][2]
            return [torch.LongTensor(s1_encoded), torch.LongTensor(s2_encoded), torch.LongTensor([label])]
        else:
            label =  self.sents[idx][1]
            return [torch.LongTensor(s1_encoded),  torch.LongTensor([label])]



class TNTrainer:
    def __init__(self, output_file, emb_dimension=100, batch_size=32, window_size=5, iterations=3,
                 initial_lr=0.01, min_count=25,weight_decay = 0,max_seq=128, pair_pattern = True):
        self.output_file_name = output_file
        if not os.path.exists(self.output_file_name):
            os.mkdir(self.output_file_name)
        
        self.emb_dimension = emb_dimension
        self.batch_size = batch_size
        self.iterations = iterations
        self.initial_lr = initial_lr
        self.weight_decay = weight_decay
        self.pair_pattern = pair_pattern
        print(args)

        reader = DataReader( vocab= vocab,max_seq=max_seq)
        self.emb_size = len(reader.word2id)

        train, test = get_sentence_pair_dataset() if pair_pattern else get_sentence_dataset()
        train, test = TNDataset(data =reader,sents =  train) , TNDataset(data =reader,sents =  test)

        self.traindataloader = DataLoader(train, batch_size=batch_size, shuffle=True, num_workers=0)

        self.testdataloader = DataLoader(test, batch_size=batch_size, shuffle=False, num_workers=0)

        self.model = Match(d= self.emb_dimension,vocab_size=vocab_size) if pair_pattern else TN(d= self.emb_dimension,vocab_size=vocab_size)

        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cuda" if self.use_cuda else "cpu")
        if self.use_cuda:
            print("using cuda and GPU ....")
            self.model.cuda()


    def train(self):
        # loss_fn = F.cross_entropy
        # loss_fn = torch.nn.CrossEntropyLoss  # for logits and target
        loss_fn = torch.nn.BCEWithLogitsLoss()  # for logits and target


        print(os.path.join(self.output_file_name,"log.txt"))
        optimizer = optim.Adam(self.model.parameters(), lr=self.initial_lr, weight_decay = self.weight_decay)

        with open("{}/log.txt".format(self.output_file_name,"log.txt"),"w") as f: 
            for iteration in range(self.iterations):

                # print("\n\n\nIteration: " + str(iteration + 1))
                print("Iteration: {}  train {} eval {}".format( iteration + 1, trainer.eval(dataloader=self.traindataloader), trainer.eval(dataloader=self.testdataloader)))
                # optimizer = optim.SparseAdam(self.skip_gram_model.parameters(), lr=self.initial_lr)
                
                # scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, len(self.dataloader))

                running_loss = 0.0
                # for i, sample_batched in enumerate(tqdm(self.traindataloader)):
                for i, sample_batched in enumerate(self.traindataloader):

                    if len(sample_batched[0]) > 1:
                        optimizer.zero_grad()
                        s1 = sample_batched[0].to(self.device)
                        if self.pair_pattern:
                            s2 = sample_batched[1].to(self.device)
                            label = sample_batched[2].to(self.device)
                            predicted = self.model.forward(s1, s2)
                        else:
                            label = sample_batched[1].to(self.device)
                            predicted = self.model.forward(s1)
 
                        emp_loss = loss_fn(predicted, label.squeeze().float())
                        str_loss = self.model.get_structure_penalty() * args.lambda_rate 
                        loss = str_loss + emp_loss
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 0.1)
                        optimizer.step()

                        if  i % args.log_step == 0: 
                            f.write("Loss in {0} steps: {1:.3f}  and empirial loss {2:.3f}  and structure loss {3:.3f}\n".format(i,loss.item(),emp_loss.item(),str_loss.item()))
                        if args.verbose:
                            print("Loss in {0} steps: {1:.3f}  and empirial loss {2:.3f}  and structure loss {3:.3f}".format(i,loss.item(),emp_loss.item(),str_loss.item()))




    def eval(self,dataloader = None):
        if dataloader is None:
            dataloader = self.traindataloader
        self.model.eval()
        results = []
        # for i, sample_batched in enumerate(tqdm(dataloader)):
        for i, sample_batched in enumerate(dataloader):
            s1 = sample_batched[0].to(self.device)
            if self.pair_pattern:
                s2 = sample_batched[1].to(self.device)
                label = sample_batched[2].to(self.device)
                predicted = torch.sigmoid(self.model.forward(s1, s2))
            else:                
                label = sample_batched[1].to(self.device)
                predicted = torch.sigmoid(self.model.forward(s1))
            results.extend(((predicted-0.5)*(label-0.5) >0).cpu().numpy())

        self.model.train()
        # print(results)
        return np.mean([np.sum(r)/len(r) for  r in results])


if __name__ == '__main__':
    
    if args.do_eval:
        pass
    else:

        trainer = TNTrainer(output_file=args.output,batch_size =args.batch_size,emb_dimension =args.emb_dimension, initial_lr = args.lr,weight_decay =args.weight_decay,max_seq = args.max_seq,iterations=args.iterations,pair_pattern =args.pair_pattern)
        
        trainer.train()


        exit()














        

