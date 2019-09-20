clc

% in= Sinal;
in=Sinal;
%  out=lopass_butterworth(T_o,0.2,10,2);
 out=T_o;
% out=t_o;
% fator de decimação a ser usado
fd=1;

% período de amostragem em segundos
Ts=fd*1;


% referir os dados ao ponto de operação em que foi feito o teste

[a b]=size(in);
[c d]=size(out);
u=in(1:fd:a);
y=out(1:fd:c);

% condições iniciais
P=eye(4)*10^6;
ini=3;
% teta99(:,ini-1)=[1.918;-0.9191;-0.0219;0.0154];
teta99(:,ini-1)=[0.01;0.01;0.01;0.01];
xi(1,ini-1)=0;      % vetor de resíduos
mse99=0;
yhat99(ini-1)=y(ini-1);       % aqui a saída ainda não foi estimada
yhat99(ini-2)=y(ini-2);       % então são usados valores medidos

% fator de esquecimento 0.835 e fd=1
%fator de esquecimento 0.8502 e fd=1 para o sinal completo
% lambda=0.8502;
lambda=0.930302;

% Algoritmo recursivo
for k=ini:length(y);
   psi_k=[y(k-1);y(k-2);u(k-1);u(k-2)];
   K_k = (P*psi_k)/((psi_k'*P*psi_k)+1);
   teta99(:,k)=teta99(:,k-1)+K_k*(y(k)-psi_k'*teta99(:,k-1));
   P=(P-((P*(psi_k*psi_k')*P)/(psi_k'*P*psi_k+lambda)))/lambda;
   yhat99(k)=[yhat99(k-1);yhat99(k-2);u(k);u(k-1)]'*teta99(:,k);   % valor predito(estimado) utilizando dados passados
   xi(k)=y(k)-yhat99(k);  % resíduo
   mse99=(xi(k))^2+mse99;   % esse somatório é utilizado para calcular o MSE
end;
teta=zeros(4,length(y));
for h=1:4
    teta(h,:)=lopass_butterworth(teta99(h,:),0.05,Ts,2);
end

erro99=mse99/(length(y));

figure(1)
subplot(2,1,1);
plot(teta(1,:),'b');
hold on;
plot(teta(2,:),'r');
plot(teta(3,:),'g');
plot(teta(4,:),'m');
xlabel('Tempo (s)');
ylabel('Parâmetros Filtrados');
legend('\theta_{1}','\theta_{2}','\theta_{3}','\theta_{4}');
subplot(2,1,2);
plot(teta99(1,:),'b');
hold on
plot(teta99(2,:),'r');
plot(teta99(3,:),'g');
plot(teta99(4,:),'m');
xlabel('Tempo (s)');
ylabel('Parâmetros');

legend('\theta_{1}','\theta_{2}','\theta_{3}','\theta_{4}');
hold off

figure(2)
plot(y','b');
hold on
plot(yhat99,'r')
hold off
xlabel('Tempo(s)')
ylabel('Temperatura')

legend('Medido filtrado','Simulado')