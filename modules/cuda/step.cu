#define THREADS _THREADS_
#define PROX _PROX_

__global__ void step(
  int n,
  int nz,
  int zone_leap,
  float *xy,
  float *dxy,
  float *tmp,
  float *link_len,
  int *links,
  int *zone_num,
  int *zone_node,
  float stp,
  float reject_stp,
  float spring_stp,
  float near_rad,
  float far_rad
){
  const int i = blockIdx.x*THREADS + threadIdx.x;

  if (i>=n){
    return;
  }

  const int ii = 2*i;

  const int zi = (int)floor(xy[ii]*nz);
  const int zj = (int)floor(xy[ii+1]*nz);

  float sx = 0.0f;
  float sy = 0.0f;
  float dx = 0.0f;
  float dy = 0.0f;
  float dd = 0.0f;
  float force;


  int j;
  int jj;
  int zk;

  int cand_count = 0;
  int total_count = 0;

  int proximity[PROX];
  tmp[i] = 0.0f;

  for (int a=max(zi-1,0);a<min(zi+2,nz);a++){
    for (int b=max(zj-1,0);b<min(zj+2,nz);b++){
      zk = a*nz+b;
      for (int k=0;k<zone_num[zk];k++){

        j = zone_node[zk*zone_leap+k];

        if ((i==j) || (j == links[ii]) || (j == links[ii+1])){
          continue;
        }

        jj = 2*j;
        total_count += 1;
        dx = xy[ii] - xy[jj];
        dy = xy[ii+1] - xy[jj+1];
        dd = sqrt(dx*dx+dy*dy);

        if (dd<far_rad && dd>0.0f){
          proximity[cand_count] = j;
          cand_count += 1;
        }
      }
    }
  }

  for (int k=0;k<cand_count;k++){

    j = proximity[k];
    jj = 2*j;

    dx = xy[ii] - xy[jj];
    dy = xy[ii+1] - xy[jj+1];
    dd = sqrt(dx*dx + dy*dy);

    if (dd>0.0f){
      force = (far_rad/dd-1.0);
      sx += force*dx*reject_stp;
      sy += force*dy*reject_stp;
    }
  }

  for (int k=0;k<2;k++){
    j = links[ii+k];
    dx = xy[ii] - xy[2*j];
    dy = xy[ii+1] - xy[2*j+1];
    dd = sqrt(dx*dx + dy*dy);
    link_len[ii+k] = dd;
    if (dd>near_rad){
      sx -= dx/dd*spring_stp;
      sy -= dy/dd*spring_stp;
      tmp[i] = (float)dd;
    }
  }

  dxy[ii] = sx*stp;
  dxy[ii+1] = sy*stp;
  tmp[i] = (float)cand_count;

}

