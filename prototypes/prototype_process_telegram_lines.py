telegram_lines = [b'OK\r\n', b'\n', b'SVFS:0000.000;0000.00;00;00;   NP;   C;-9.999;20000;00059;12773;00000;012;450994;2.11.6;2.11.1;0.50;24.3;0;14:09:59;16.02.2023;;;0000.00;000;025;013;013;00.000;0000.0;0000.00;-9.99;0000.00;0000.00;00000007;\n', b'F90:-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;-9.999;\n', b'F91:00.000;00.000;00.000;00.000;00.000;\n', b'F93:000;000;000;000;000;000;\n', b'F61:00.502;00.853\r\n', b'00.606;02.026\r\n', b'00.550;01.595\r\n', b'00.521;01.237\r\n', b'00.540;01.070\r\n', b'00.559;01.710\r\n', b'00.571;01.572\r\n', b';']

# options are 
# *  to merge all itemes following F61: item into a single item

def join_f61_items(telegram_list):
    '''
    def uses the telegram_list index, of where F61 is positioned
    to mark th start of F61 items in telegram_list.
    Those items (with exception iog last, empty item) are return in the list of string f61_items

    Each one of the f61_items will be a row, with 2 columns (3 if we include timestamp).
    '''
    for index, item in enumerate(telegram_list):
        if 'F61:' in item.decode('utf-8'):
            f61_items = telegram_list[index:-1]  
            f61_items = [item.decode('utf-8').replace('\r\n', '').replace('F61:','') for item in f61_items]
            f61_items = f61_items
    return f61_items

f61_items = join_f61_items(telegram_list=telegram_lines)
print(f61_items)
'''
what is the best output format to get the function from returning them?
* list of lists
* list of tuples
* list of string <- will try this one first seems most intuitive

'''