/* CRILAYLA decoder. Format reference: kamikat/cpktools cpk/crilayla.py.
 * Optional native accelerator for cpk_extract.py. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif
typedef struct { const uint8_t *data; ptrdiff_t pos; unsigned bits, left; int failed; } bits_t;
static unsigned readbits(bits_t *b, unsigned n) {
    unsigned result=0;
    while(n--) {
        if(!b->left) {
            if(b->pos<16) { b->failed=1; return 0; }
            b->bits=b->data[b->pos--]; b->left=8;
        }
        result=(result<<1)|((b->bits>>(--b->left))&1);
    }
    return result;
}
EXPORT int cpk_crilayla(const uint8_t *data, size_t input_size, uint8_t *out, size_t out_size) {
    if(input_size<16 || memcmp(data,"CRILAYLA",8)) return 1;
    uint32_t size=(uint32_t)data[8]|((uint32_t)data[9]<<8)|((uint32_t)data[10]<<16)|((uint32_t)data[11]<<24);
    uint32_t packed=(uint32_t)data[12]|((uint32_t)data[13]<<8)|((uint32_t)data[14]<<16)|((uint32_t)data[15]<<24);
    if((size_t)size+256!=out_size || (size_t)packed+272>input_size) return 2;
    memcpy(out,data+16+packed,256);
    bits_t b={data,(ptrdiff_t)16+packed-1,0,0,0};
    ptrdiff_t pos=(ptrdiff_t)out_size-1;
    while(pos>=256 && !b.failed) {
        if(!readbits(&b,1)) out[pos--]=(uint8_t)readbits(&b,8);
        else {
            unsigned offset=readbits(&b,13)+3,length=3,extra=0;
            const unsigned widths[]={2,3,5,8};
            unsigned index;
            for(index=0;index<4;index++) {
                extra=readbits(&b,widths[index]); length+=extra;
                if(extra!=(1u<<widths[index])-1) break;
            }
            if(index==4) { do { extra=readbits(&b,8); length+=extra; } while(extra==255 && !b.failed); }
            if(length>(size_t)pos-255 || (size_t)pos+offset>=out_size) return 3;
            while(length--) { out[pos]=out[pos+offset]; pos--; }
        }
    }
    return b.failed?4:0;
}
