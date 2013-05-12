def __get_fs_old(top):
    '''
    return: set of full patchs
    '''
    PATHS = list()
    toplen = len(top)
    ISDIR = re.compile(top+'/[0-9A-F]{2}/[0-9A-F]{2}/[0-9A-F]{2}/[0-9A-F]{2}')
    for root, dirs, files in os.walk(top):
        #print root, len(dirs), len(files),
        if (ISDIR.match(root)):
            id = __dir2id(root[toplen+1:])
            for i in files:
                PATHS.append(unicode(os.path.join(root, i)))
    PATHS.sort()
    return set(PATHS)

def _chk_old(db, root, full=False, force=False):
    '''
    Outbox/Yesterday:
    + lost dir
    + lost file
    - extra dir
    + extra file
    + cmp (size[, md5])  # fname, mtime
    '''
    errors = 0
    updates = dict()
    paths = __get_fs(root)
    #pprint.pprint(paths)
    for id, src in db.iteritems():
        dst = paths.get(id, None)
        if (not dst):
            # 1. lost dir
            print 'Dir %08X is absent' % id
            errors += 1
        else:
            # 2. lost file
            if (not src['fname'] in dst):
                print 'File %08X ("%s") is absent' % (id, src['fname'])
                errors += 1
            else:
                # 3. extra files
                if (len(dst) > 1):  # extra files exists
                    for j in dst:
                        if (not src['fname'] == j):     # skip main file
                            path = __mkpath(root, id, j)
                            print 'Delete extra file: "%s"' % path
                            if (force):
                                os.remove(path)
                del paths[id]
                # 4. check
                path =  __mkpath(root, id, src['fname'])
                # 4.1. fast
                size = os.path.getsize(path)
                if (size != src['size']):
                    print 'Wrong size of %08X (%d instead of %d)' % (id, size, src['size'])
                    updates[id] = dict()
                    updates[id]['size'] = size
                # 4.2. md5
                if (full):
                    md5 = __file_md5(path)
                    if (md5 != src['md5']):
                        print 'Wrong md5 of %08X (%s instead of %s)' % (id, md5, src['md5'])
                        if (not id in updates):
                            updates[id] = dict()
                        updates[id]['md5'] = md5
    # X. extra dirs
    for i in paths.keys():
        path = __mkpath(root, i, '')
        print 'Delete extra dir: "%s"' % path
        if (force):
            shutil.rmtree(path)
            #os.remove(path)
    #pprint.pprint(paths)
    return errors, updates

