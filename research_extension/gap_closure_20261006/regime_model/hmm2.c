#include <math.h>
#include <stdlib.h>
static double ladd(double x,double y){double m=fmax(x,y);return m+log(exp(x-m)+exp(y-m));}
int hmm2(long n,const double *e,const double *P,const double *pi,double *g,double *xi,double *filtered,double *lik){
 double *a=malloc(2*n*sizeof(double)),*b=calloc(2*n,sizeof(double));
 if(!a||!b){free(a);free(b);return 1;}
 double lp[4];for(int j=0;j<4;j++)lp[j]=log(P[j]);
 a[0]=log(pi[0])+e[0];a[1]=log(pi[1])+e[1];
 for(long t=1;t<n;t++)for(int j=0;j<2;j++)a[2*t+j]=e[2*t+j]+ladd(a[2*(t-1)]+lp[j],a[2*(t-1)+1]+lp[2+j]);
 *lik=ladd(a[2*n-2],a[2*n-1]);
 for(long t=n-2;t>=0;t--)for(int i=0;i<2;i++)b[2*t+i]=ladd(lp[2*i]+e[2*(t+1)]+b[2*(t+1)],lp[2*i+1]+e[2*(t+1)+1]+b[2*(t+1)+1]);
 for(long t=0;t<n;t++){double norm=ladd(a[2*t],a[2*t+1]);for(int j=0;j<2;j++){g[2*t+j]=exp(a[2*t+j]+b[2*t+j]-*lik);filtered[2*t+j]=exp(a[2*t+j]-norm);}}
 for(long t=0;t<n-1;t++)for(int i=0;i<2;i++)for(int j=0;j<2;j++)xi[4*t+2*i+j]=exp(a[2*t+i]+lp[2*i+j]+e[2*(t+1)+j]+b[2*(t+1)+j]-*lik);
 free(a);free(b);return 0;
}
