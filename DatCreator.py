def dat_creator(iter_data, path):
    f = open(path, 'w')
    for item in iter_data:
        f.write(str(item))
        f.write('\n')
    f.close()


def metadata_creator(iter_data_columns, path):
    f = open(path, 'w')
    for row_num in range(len(iter_data_columns[0])):
        row = ''
        for column in iter_data_columns:
            row += str(column[row_num])
            row += '\t'
        f.write(row)
        f.write('\n')
    f.close()


def toml_creator(columns, path):
    f = open(path, 'w')
    f.write('''type = "line-corpus"''')
    f.write('\n')


def files_creator(iter_names, iter_files, path):
    f = open(path + 'descriptions-full-corpus.txt','w')
    for row_num in range(len(iter_names)):
        name_id = iter_names[row_num]
        row = name_id + ' ' + name_id + '.txt'
        f.write(row)
        f.write('\n')
        corpus_f = open(path + name_id + '.txt', 'w')
        corpus_f.write(iter_files[row_num])
        corpus_f.close()
    f.close()