!!
!! file for p1.f90
!!
PROGRAM LEEOR2D
   INTEGER :: I, CYL, DT2, DT, GX, GY, NL_PREDCOR, ITER_COUNTER, J, MISHOR, NL_SUBZONAL, NL_STRESS, NL_VERT_MASS, NL_SYMMETRY, NYP &
   , NXP, NLCARAMANA, NX, NY
   REAL*8 :: R4, DTGX, DTGY, P_MULT, R1, R2, R3, RIJM, RIJ, RIPJ, RIJP, RIMJ, X1, Y1, X3, X2, X4, Y4, Y3, Y2
   REAL*8 , ALLOCATABLE :: YNS(:, :), YLAG(:, :), XNT(:, :), XNS(:, :), XLIM(:, :, :), XMC(:, :), XMQ(:, :, :), XKAPPA(:, :), XLAG &
   (:, :), XGAL(:, :), XMV(:, :), Y(:, :), YGAL(:, :), YNT(:, :), X(:, :), VOLGAS(:, :), VOLLAG(:, :), VSOUND(:, :), VMOM(:, :),  &
   VMOMP(:, :), VG(:, :), UMOM(:, :), UGAL(:, :), UMOMP(:, :), U(:, :), UG(:, :), V(:, :), TR(:, :), SYHALF(:, :, :), SIEP(:, :),  &
   SXHALF(:, :, :), SIE2(:, :), SIEGAL(:, :), S4(:, :), ROSHOCK(:, :), S3(:, :), SIE(:, :), ROGAL(:, :), ROPOINT(:, :), RO_INIT(: &
   , :), RO22(:, :), RO(:, :), RMV(:, :), RO11(:, :), SIE1(:, :), TSHOCK(:, :), RGAL(:, :), R(:, :), Q(:, :), QSCALAR(:, :, :),  &
   PIYYGAL(:, :), PIYYP(:, :), PTOT(:, :), PIXYP(:, :), PIYY(:, :), PIXXP(:, :), PIXXGAL(:, :), PIXY(:, :), PIXX(:, :), PIXYGAL(: &
   , :), PITH(:, :), PEPSPD(:, :), PITHGAL(:, :), PEPSP(:, :), PEPSPC(:, :), P(:, :), P_DEP_CELL(:, :), MV(:, :), MVP(:, :), MQ(: &
   , :, :), MP(:, :), MC(:, :), PITHP(:, :), FY(:, :, :), FX(:, :, :), FTM(:, :), EPSP(:, :), EPSPC(:, :), EPSPD(:, :), CPOINT(:,  &
   :), CDPDRO(:, :), CDPDE(:, :), AYHALF(:, :, :), AXHALF(:, :, :), AX(:, :), AY(:, :), DC_B(:, :), DC_BP(:, :), VGAL(:, :)
   IF (NL_VERT_MASS.EQ.2) THEN
!$omp parallel do private(I, RIPJ, RIMJ, RIJP, RIJM, RIJ)
      DO 25 J = 1, NYP
         DO 23 I = 1, NXP
            RIJ = DBLE(1-MISHOR)*R(I,J)+DBLE(MISHOR)
            RIPJ = DBLE(1-MISHOR)*R(I+1,J)+DBLE(MISHOR)
            RIJP = DBLE(1-MISHOR)*R(I,J+1)+DBLE(MISHOR)
            RIMJ = DBLE(1-MISHOR)*R(I-1,J)+DBLE(MISHOR)
            RIJM = DBLE(1-MISHOR)*R(I,J-1)+DBLE(MISHOR)
            AX(I,J) = -(1.25e-01*DT2*RMV(I,J)*((Y(I+1,J)-Y(I,J))*(3*RIJ+RIPJ)*(PTOT(I,J-1)-PTOT(I,J))+(Y(I,J+1)-Y(I,J))*(3*RIJ+ &
            RIJP)*(PTOT(I,J)-PTOT(I-1,J))+(Y(I-1,J)-Y(I,J))*(3*RIJ+RIMJ)*(PTOT(I-1,J)-PTOT(I-1,J-1))+(Y(I,J-1)-Y(I,J))*(3*RIJ+RIJM &
            )*(PTOT(I-1,J-1)-PTOT(I,J-1))))
            AY(I,J) = 1.25e-01*DT2*RMV(I,J)*((X(I+1,J)-X(I,J))*(3*RIJ+RIPJ)*(PTOT(I,J-1)-PTOT(I,J))+(X(I,J+1)-X(I,J))*(3*RIJ+RIJP) &
            *(PTOT(I,J)-PTOT(I-1,J))+(X(I-1,J)-X(I,J))*(3*RIJ+RIMJ)*(PTOT(I-1,J)-PTOT(I-1,J-1))+(X(I,J-1)-X(I,J))*(3*RIJ+RIJM)*( &
            PTOT(I-1,J-1)-PTOT(I,J-1)))
23                CONTINUE
25             CONTINUE
   ELSE
!$omp parallel do private(I, RIPJ, RIMJ, RIJP, RIJM, RIJ)
      DO 20 J = 1, NYP
         DO 10 I = 1, NXP
            RIJ = DBLE(1-MISHOR)*R(I,J)+DBLE(MISHOR)
            RIPJ = DBLE(1-MISHOR)*R(I+1,J)+DBLE(MISHOR)
            RIJP = DBLE(1-MISHOR)*R(I,J+1)+DBLE(MISHOR)
            RIMJ = DBLE(1-MISHOR)*R(I-1,J)+DBLE(MISHOR)
            RIJM = DBLE(1-MISHOR)*R(I,J-1)+DBLE(MISHOR)
            AX(I,J) = 5.e-01*DT2*RIJ*RMV(I,J)*(PTOT(I-1,J)*(Y(I,J+1)-Y(I-1,J))-PTOT(I,J)*(Y(I,J+1)-Y(I+1,J))-PTOT(I,J-1)*(Y(I+1,J) &
            -Y(I,J-1))+PTOT(I-1,J-1)*(Y(I-1,J)-Y(I,J-1)))
            AY(I,J) = 2.5e-01*DT2*RMV(I,J)*((-(PTOT(I-1,J)*(X(I,J+1)-X(I-1,J))*(RIJP+RIMJ)))+PTOT(I,J)*(X(I,J+1)-X(I+1,J))*(RIJP+ &
            RIPJ)+PTOT(I,J-1)*(X(I+1,J)-X(I,J-1))*(RIPJ+RIJM)-PTOT(I-1,J-1)*(X(I-1,J)-X(I,J-1))*(RIMJ+RIJM))
10                CONTINUE
20             CONTINUE
   ENDIF
60       CONTINUE
END PROGRAM LEEOR2D
