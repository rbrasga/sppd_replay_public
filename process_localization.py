import sys
import codecs
codecs.register_error("strict", codecs.ignore_errors)
import os
import json

def getAssetName(filename,asset_path):
	asset_name=None
	asset_desc=None
	fh = open(os.path.join(asset_path, filename),"r",encoding='utf8')
	json_string = fh.read()
	result = None
	try:
		result = json.loads(json_string)
	except Exception as e:
		print(str(e))
		print(f'[ERROR] Unable to parse JSON in {filename}')
		sys.exit(1)
	if 'Image' in result:
		asset_name = result['Image'].replace('PF','').replace('Char','').replace('Card','').upper()
	if 'OasisNameOverride' in result and result['OasisNameOverride'] != '':
		asset_name = result['OasisNameOverride'].replace('DF_NAME_','')
	if 'OasisDescOverride' in result and result['OasisDescOverride'] != '':
		asset_desc = result['OasisDescOverride'].replace('DF_DESC_','')
	if asset_desc == None: asset_desc = asset_name
	return asset_name, asset_desc

mypath = r'C:\Users\Remin\Documents\GitHub\sppd-data\localisation\localisation.txt'

input_file = open(mypath,'rb')
input_lines = input_file.read().decode('utf-8').split('\n')

write_to_file = 'LOCAL={}\n'
index = 0
for line in input_lines:
	split_text = []
	try:
		split_text = line.split('\t')
		#print(split_text)
		index+=1
	except Exception as e:
		#print(str(e))
		#print(f"Unable to read {line}")
		print(f"Unable to read {index}")
		index+=1
		#sys.exit()
		continue
	if len(split_text) != 13:
		continue
	NAME = split_text[1]
	if not ("DF_NAME" in NAME or "DF_DESC" in NAME):
		continue
	NAME = f'"{NAME}"'
	'''
	Angel Wendy		ENGLISH
	Wendy l'Ange	FRENCH
	Engel-Wendy		GERMAN
	Wendy l'Angelo	ITALIAN
	天使ウェンディ		JAPANESE
	천사 웬디			KOREAN
	Ангел Венди		RUSSIAN
	Wendy Ángel		SPANISH
	Wendy Anjinha	BRAZILIAN
	Wendy Anioł		POLISH
	'''
	write_to_file+=f'LOCAL[{NAME}]=[]\n'
	for i in range(2,12):
		language_text = split_text[i]
		if "'" in language_text and '"' in language_text:
			print(f'[ERROR] {NAME}')
		elif '"' in language_text:
			write_to_file+=f"LOCAL[{NAME}].append(r'{language_text}')\n"
		else:
			write_to_file+=f'LOCAL[{NAME}].append(r"{language_text}")\n'

# Get the asset names
asset_path = r'C:\Users\Remin\Documents\GitHub\sppd-data\cards'
onlyfiles = [f for f in os.listdir(asset_path) if os.path.isfile(os.path.join(asset_path, f))]
write_to_file += 'ASSET={}\n'
for filename in onlyfiles:
	split_fn = filename.split('_') #CardId_2251_StuartSciCard.json
	try:
		if len(split_fn) != 3 or \
		int(split_fn[1]) < 0: continue
	except:
		print(f'unknown cardid: {split_fn[1]}')
		continue
	if 'json' not in filename: continue
	CARD_ID=int(split_fn[1])
	asset_name,asset_desc=getAssetName(filename,asset_path)
	if asset_name == None or asset_name == '': continue
	if asset_name == asset_desc:
		write_to_file+=f'ASSET[{CARD_ID}]="{asset_name}"\n'
	else:
		write_to_file+=f'ASSET[{CARD_ID}]=["{asset_name}","{asset_desc}"]\n'
		
output_file = open('LOCALIZATION.py', 'wb')
output_file.write(write_to_file.encode('utf-8'))
output_file.close()