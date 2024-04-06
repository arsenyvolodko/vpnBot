from classes_util.Ips import Ips
from shared import botDB
from tqdm import tqdm

for i in tqdm(range(11, 256)):
    botDB.add_free_ips(Ips(f'10.66.66.{i}'))
