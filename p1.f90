PROGRAM LEEOR2D

 
REAL(8), ALLOCATABLE :: PTOT(:,:), Y(:,:), X(:,:), R(:,:), U(:,:),V(:,:), &
      MC(:,:),MV(:,:),RO(:,:),P(:,:),SIE(:,:),Q(:,:), &
      PIXX(:,:), &
       PIXY(:,:),PIYY(:,:),PITH(:,:),RMV(:,:),EPSP(:,:),XMV(:,:)       &
      ,XMC(:,:),VSOUND(:,:),AX(:,:),AY(:,:),CDPDE(:,:),CDPDRO(:,:)     &
      ,XLAG(:,:),YLAG(:,:),UG(:,:),VG(:,:)        &
      ,TR(:,:)     &
      ,DC_B(:,:),XKAPPA(:,:),DC_BP(:,:)         &
      ,UMOM(:,:),VMOM(:,:),UMOMP(:,:),VMOMP(:,:),MP(:,:),SIEP(:,:)     &
      ,PIXXP(:,:),PIXYP(:,:),PIYYP(:,:),PITHP(:,:),MVP(:,:),PEPSP(:,:) &
      ,VOLGAS(:,:) &
      ,XNT(:,:),YNT(:,:) &
      ,VOLLAG(:,:),FTM(:,:),S3(:,:),S4(:,:),XNS(:,:),YNS(:,:)          &
      ,TSHOCK(:,:),RO_INIT(:,:),ROSHOCK(:,:),RO11(:,:),RO22(:,:)       &
      ,SIE1(:,:),SIE2(:,:),EPSPD(:,:),EPSPC(:,:)           &
      ,PEPSPD(:,:),PEPSPC(:,:)                                         &
      ,XGAL(:,:),YGAL(:,:),RGAL(:,:),UGAL(:,:),VGAL(:,:)               &
      ,SIEGAL(:,:),ROGAL(:,:),PIXXGAL(:,:),PIXYGAL(:,:)                &
      ,PIYYGAL(:,:),PITHGAL(:,:)                                       &
      ,ROPOINT(:,:),CPOINT(:,:),P_dep_cell(:,:)                        &
      ,MQ(:,:,:),XMQ(:,:,:),FX(:,:,:),FY(:,:,:)                        &
      ,QSCALAR(:,:,:),XLIM(:,:,:),AXHALF(:,:,:),AYHALF(:,:,:)          &
      ,SXHALF(:,:,:),SYHALF(:,:,:)


      REAL(8) :: RIJ,RIPJ,RIJP,RIMJ,RIJM,DTGX,DTGY
      REAL(8) :: X1,X2,X3,X4,Y1,Y2,Y3,Y4,R1,R2,R3,R4,P_MULT
      INTEGER :: I,J,NY,NYP,NXP,NX,NL_VERT_MASS,NL_SYMMETRY,NL_SUBZONAL,NL_STRESS &
,NLCARAMANA,NL_PREDCOR,ITER_COUNTER,GX,GY,MISHOR,DT2,DT,CYL
! +++
! +++ PHASE 1. EXPLICIT LAGRANGIAN CALCULATION,IN WHICH HE ADJUST
! +++ THE LAGRANGIAN VELOCITIES BY PRESSURE GRADIENTS AND BODY FORCES.  
! +++
! +++ THE PRESSURE ACCELERATIONS. THE ACCELERATIONS ARE NOT DIRECTLY
! +++ ADDED TO THE VELOCITIES, BUT ARE REMEMBERED IN VECTORS AX,AY.
! +++ THESE ARE LATER USED IN SUBR. AVISC TO CALCULATE THE SHOCK
! +++ DIRECTION AND THE ARTIFICIAL VISCOSITY.
! +++
 
        IF(NL_VERT_MASS.EQ.2) THEN

        DO 25 J=1,NYP
        DO 23 I=1,NXP
          RIJ=DBLE(1-MISHOR)*R(I,J)+DBLE(MISHOR)
          RIPJ=DBLE(1-MISHOR)*R(I+1,J)+DBLE(MISHOR)
          RIJP=DBLE(1-MISHOR)*R(I,J+1)+DBLE(MISHOR)
          RIMJ=DBLE(1-MISHOR)*R(I-1,J)+DBLE(MISHOR)
          RIJM=DBLE(1-MISHOR)*R(I,J-1)+DBLE(MISHOR)
          AX(I,J)=-0.125D0*DT2*RMV(I,J)*(                            &
           (Y(I+1,J)-Y(I,J))*(3D0*RIJ+RIPJ)*(PTOT(I,J-1)-PTOT(I,J))+       &
           (Y(I,J+1)-Y(I,J))*(3D0*RIJ+RIJP)*(PTOT(I,J)-PTOT(I-1,J))+       &
           (Y(I-1,J)-Y(I,J))*(3D0*RIJ+RIMJ)*(PTOT(I-1,J)-PTOT(I-1,J-1))+   &
           (Y(I,J-1)-Y(I,J))*(3D0*RIJ+RIJM)*(PTOT(I-1,J-1)-PTOT(I,J-1)))
          AY(I,J)=0.125D0*DT2*RMV(I,J)*(                             &
           (X(I+1,J)-X(I,J))*(3D0*RIJ+RIPJ)*(PTOT(I,J-1)-PTOT(I,J))+       &
           (X(I,J+1)-X(I,J))*(3D0*RIJ+RIJP)*(PTOT(I,J)-PTOT(I-1,J))+       &
           (X(I-1,J)-X(I,J))*(3D0*RIJ+RIMJ)*(PTOT(I-1,J)-PTOT(I-1,J-1))+   &
           (X(I,J-1)-X(I,J))*(3D0*RIJ+RIJM)*(PTOT(I-1,J-1)-PTOT(I,J-1)))
23      CONTINUE
25      CONTINUE
! 2. WITH "DIAMOND" CONTROL VOLUMES:
      ELSE
        DO 20 J=1,NYP
        DO 10 I=1,NXP
          RIJ=DBLE(1-MISHOR)*R(I,J)+DBLE(MISHOR)
          RIPJ=DBLE(1-MISHOR)*R(I+1,J)+DBLE(MISHOR)
          RIJP=DBLE(1-MISHOR)*R(I,J+1)+DBLE(MISHOR)
          RIMJ=DBLE(1-MISHOR)*R(I-1,J)+DBLE(MISHOR)
          RIJM=DBLE(1-MISHOR)*R(I,J-1)+DBLE(MISHOR)
          AX(I,J)=0.5D0*DT2*RIJ*RMV(I,J)*(                           &
          PTOT(I-1,J)*(Y(I,J+1)-Y(I-1,J))-                              &
          PTOT(I,J)*(Y(I,J+1)-Y(I+1,J))-                                &
          PTOT(I,J-1)*(Y(I+1,J)-Y(I,J-1))+                              &
          PTOT(I-1,J-1)*(Y(I-1,J)-Y(I,J-1)))
          AY(I,J)=0.25d0*DT2*RMV(I,J)*(                              &
          -PTOT(I-1,J)*(X(I,J+1)-X(I-1,J))*(RIJP+RIMJ)+                 &
          PTOT(I,J)*(X(I,J+1)-X(I+1,J))*(RIJP+RIPJ)+                    &
          PTOT(I,J-1)*(X(I+1,J)-X(I,J-1))*(RIPJ+RIJM)-                  &
          PTOT(I-1,J-1)*(X(I-1,J)-X(I,J-1))*(RIMJ+RIJM))
10      CONTINUE
20      CONTINUE
      end if
      60    CONTINUE


     
      END PROGRAM LEEOR2D
