import zlib, struct, sys, glob
def readpng(fn):
    d=open(fn,'rb').read(); i=8; idat=b''
    while i<len(d):
        n=struct.unpack('>I',d[i:i+4])[0]; t=d[i+4:i+8]
        if t==b'IHDR': w,h=struct.unpack('>II',d[i+8:i+16])
        if t==b'IDAT': idat+=d[i+8:i+8+n]
        i+=12+n
    raw=zlib.decompress(idat); rows=[raw[y*(w*3+1)+1:(y+1)*(w*3+1)] for y in range(h)]
    return w,h,rows
def writepng(fn, rows, w, h):
    def ch(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(fn,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(b''.join(b'\0'+r for r in rows)))+ch(b'IEND',b''))
def montage(files, out, x0=0, y0=0, x1=160, y1=152, sc=1):
    ims=[readpng(f) for f in files]
    rows=[]
    for y in range(y0, y1):
        r=b''
        for w,h,rr in ims:
            seg=rr[y][x0*3:x1*3]
            r+=b''.join(seg[i*3:i*3+3]*sc for i in range(x1-x0))
        for _ in range(sc): rows.append(r)
    writepng(out, rows, (x1-x0)*sc*len(ims), (y1-y0)*sc)
if __name__=='__main__':
    pat, out = sys.argv[1], sys.argv[2]; x0,y0,x1,y1,sc = map(int, sys.argv[3:8])
    montage(sorted(glob.glob(pat)), out, x0,y0,x1,y1,sc)
