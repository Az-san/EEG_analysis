%%%　脳波解析プログラム（徳田先生の解析用プログラム）EEGLABのデータロード時に、電極配置ファイルをロードしている。
%%%　　　重本作成、2021.8.5 夏目改訂
%%%      夏目改訂　2021.8.21　EEGlabで瞬き削除出来るようにする
%%%　Signal Processing　Toolboxをインストールしておく必要がある。これはMatlabの「ホーム」「アドオン」「アドオンの管理」から確認する
%%%     2021.10.12 　斉藤さん用に改変（Intercross413測定ソフト、ハードはIntercross415で、ジャイロ等の設定をNo measureにする。）すると、データ保存の時ｍ保存されない。
%%%  2022/4/22 澤田インタークロスデータ用（2000Hzサンプル用に書き直す）DCフィルターがカットされているので、以上にドリフトしている。
%%%  2022/10/4 Subplotの所でチャネル数が奇数偶数でバグがあったので修正した。 
%%% 2022/11/8 Signal Processing Toolboxが必要である。Matlabインストール時にインストールするか、もし忘れた場合、「ホーム」「アドオン」からインストする。もしインストールされていなければ、risampleでエラーが出る。
%%% 2022/11/20 溝上さん消防士脳波データもこのプログラムで解析する。
%%% EEglabはMatlab2022版では動かないようである。
%%% 2023/9/27　徳田先生・大西さんとの共同研究での脳波測定データに対応するように変更する。マーク時間を抽出し、その時間間脳波データをクリップして解析する。
%%% 2023/10/12 北川用に改変
%%% 2023/12/5 岩本改変
%%% 2025/1/6 工藤改変 迷路探索システム解析用に

clear all;

%%format short;
%%
%% 初期設定
%% サンプリング周波数Fsは1000Hz
Fs = 1000;
FFT_Fs = 1024;
total_channel_number = 8;
EEG_channel_number = 8; %% 残りのチャネルはTTL, EOG, ECG等
extra_data = 0; %% ジャイロセンサーなど測定ONにしているとここに数値12を入れる。not measureの時は0にする。

oldfolder = cd; %% プログラムのある場所のフォルダー名

% GUIを表示
fprintf('データの選択\n');
filter = '*.txt;*.csv';
[ fname, pathname ] = uigetfile( filter, 'ファイルを開く', 'MultiSelect', 'off' );
fprintf('%s\n',fname);
[pathstr,file_name,ext] = fileparts(fname); %% ファイル名を拡張子とファイル名に分割する。file_nameは純粋にファイル名。fnameは拡張子付きファイル名。
%% pathnameは脳波データファイルがある絶対フォルダー名

% 拡張子を取得
if strcmp(ext,'.TXT') == 1 % テキストファイルなら
    delimiterIn = ' ';
    headerlinesIn = 1;
    A = importdata(strcat(pathname, fname), delimiterIn, headerlinesIn);
    % リサンプリング
    data = resample(A.data, FFT_Fs, Fs);
else % CSVファイルなら
    data = importdata(strcat(pathname, fname));
    eegdata = data.data(:, 14:21);
    electrode_name = data.textdata(14:21);
    electrode_name = data.textdata((extra_data+2):(extra_data+EEG_channel_number+1));
    eegdata = data.data(:, (extra_data+2):(extra_data+EEG_channel_number+1));

    %% mark_timeはTimeEvent(TTL)の時間を格納する。
    mark_time = data.data(:, (extra_data+10)); mark_time = rmmissing(mark_time); %% 動画の最初と最後の時間をとる。
    resample_eegdata = resample(eegdata, FFT_Fs, Fs);
end;

cd(pathname)

%% オフセットを補正する。（DCフィルターが切れているので、この処理を入れる。）
average_resample_eegdata = mean(resample_eegdata);
resample_eegdata = resample_eegdata - average_resample_eegdata;

% 短時間FFTのスペクトログラムを表示
for i = 1:EEG_channel_number
    if rem(EEG_channel_number, 2) == 1
        subplot(fix(EEG_channel_number/2) + 1, 2, i); %% プロットする場所の指定
    else
        subplot(fix(EEG_channel_number/2), 2, i); %% プロットする場所の指定
    end
    spectrogram(resample_eegdata(:, i), FFT_Fs, FFT_Fs/2, FFT_Fs, FFT_Fs, 'yaxis');
    ylim([0 40]);
    title(electrode_name(1, i));
end;

sgtitle('Short-time FFT Spectra before ICA')
save_fig_filename = strcat(file_name, '_before ICA.jpg'); %% 自動的なファイル名作成
disp('[jpeg] Saving figure...')
saveas(gcf, save_fig_filename, 'jpeg'); %% Figureの保存

eegdata = resample_eegdata(:, 1:EEG_channel_number)';

%% eeglabに移行し、ICAでEOGを元に瞬きを除去する。
[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab; %% EEGLABの開始
EEG = pop_importdata('dataformat', 'array', 'nbchan', EEG_channel_number, 'data', 'eegdata', 'srate', FFT_Fs, 'pnts', 0, 'xmin', 0, 'chanlocs', 'C:\Users\Maiko Kudo\Documents\【IMPORTANT DATA】\20241218脳波データ\kudou.ced');
[ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, 0, 'setname', file_name, 'gui', 'off');
EEG = eeg_checkset(EEG);
[ALLEEG, EEG] = eeg_store(ALLEEG, EEG, CURRENTSET);

%% eeglabへの脳波データの表示
pop_eegplot(EEG, 1, 1, 1);
EEG = eeg_checkset(EEG);

disp('Pause... ICAの操作を行って下さい。もし終わったらスペースキーを押して下さい。After you decmpose the signal by ICA, please push space key');
pause;

%% ICAの実行
EEG = eeg_checkset(EEG);
EEG = pop_saveset(EEG, 'filename', strcat(file_name, ' pruned with ICA.set'), 'filepath', '');
EEG = eeg_checkset(EEG);

disp('Pause... ICA成分からEOG成分を見つけ、それを差し引く操作を行って下さい。もし無かったら何もしなくて良いです。その後、スペースキーを押して下さい。if you subtract EOG component from EEG, please push space key');
pause;

% 2回目のpop_savesetで、EOG成分除去後のデータを保存
EEG = pop_saveset(EEG, 'filename', strcat(file_name, ' pruned with ICA subtraction.set'), 'filepath', pathname);
EEG = eeg_checkset(EEG);

% ICA後のEEGデータを.txt形式で保存
save_txt_filename = fullfile(pathname, strcat(file_name, '_after_ICA_subtraction.txt'));
writematrix(EEG.data', save_txt_filename);
disp(['[txt] Saving EEG data to ', save_txt_filename, '... Done.']);




%%
%% どのComponentを削除するかeeglab上で決めてSubtraction（削除）する。
%%
%%[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG,
%%1,'savenew',strcat(file_name, ' pruned with ICA.set'),'gui','off'); 　 %%ファイル名の自動作成
EEG = eeg_checkset( EEG );
EEG = pop_saveset( EEG, 'filename',strcat(file_name, ' pruned with ICA subtraction.set'),'filepath',''); %%ファイル名の自動作成
EEG = eeg_checkset( EEG );

for j=1:size(FFT_video_time,1)
    k = figure;
    %%ICAかけたものの短時間FFT解析結果を出力する。-1秒～end_timeまで
    %%FFT_start_time = FFT_video_time(j,1) - 1* FFT_Fs; FFT_end_time_post = FFT_video_time(j,2);%%元プログラム
    FFT_start_time_base = FFT_video_time(j,1) - 1* FFT_Fs; FFT_end_time_base = FFT_video_time(j,1);%%ベースライン分のエポック。ベースライン２秒中の後半１秒を格納するため。
    FFT_start_time_stim = FFT_video_time(j,1) + 1* FFT_Fs; FFT_end_time_stim = FFT_video_time(j,2);%%SSVEPのエポック。刺激時間１０秒のうち、後半９秒を格納するため。
    base_data = EEG.data(:,FFT_start_time_base:FFT_end_time_base);%%ベースライン分のデータ
    stim_data = EEG.data(:,FFT_start_time_stim:FFT_end_time_stim);%%刺激時間分のデータ
    %%sFFT_EEG_data = EEG.data(:,FFT_start_time:FFT_end_time);%%元プログラム
    sFFT_EEG_data = [base_data, stim_data];
    resample_eegdata = sFFT_EEG_data';
    figure(k) %%eeglabを停止しないとこのコマンドが機能しない。
    % 短時間FFTのスペクトログラムを表示
    for i=1:EEG_channel_number
        %{
        subplot(fix(EEG_channel_number/2)+1,2,i);
        spectrogram(resample_eegdata(:,i),FFT_Fs,FFT_Fs/2,FFT_Fs,FFT_Fs,'yaxis');
        ylim([0 50]);
        title(electrode_name(1,i));
        %}
        %%
        if rem(EEG_channel_number,2) == 1 
            subplot(fix(EEG_channel_number/2)+1,2,i);
        else
            subplot(fix(EEG_channel_number/2),2,i);
        end
        spectrogram(resample_eegdata(:,i),FFT_Fs,FFT_Fs/2,FFT_Fs,FFT_Fs,'yaxis');
        ylim([0 40]);
        title(electrode_name(1,i));
    end;
    set(groot,'DefaultFigureColormap','remove') %%Figureに関して規定値に戻す。
    sfft_title = strcat('Short-time FFT Spectra after ICA No.',int2str(j));
    %%sgtitle('Short-time FFT Spectra after ICA#'+int2str(j))
    sgtitle(sfft_title)
    save_fig_filename = strcat(file_name, '_after ICA No.',int2str(j),'.jpg'); %%ファイル名の自動作成
    disp( '[jpeg] Saving figure...' )
    saveas(gcf,save_fig_filename,'jpeg'); %%Figureの保存
    %%j =1;
    save_xls_filename = strcat(file_name,'_after ICA No.',int2str(j),'.xlsx'); %%ファイル名の自動作成
    % 短時間FFTのパワーデータCH毎に保存する
    for i=1:EEG_channel_number
        [S,F,T] = spectrogram(resample_eegdata(:,i),FFT_Fs,FFT_Fs/2,FFT_Fs,FFT_Fs);
        disp( '[xlsx] Saving EEG Power data...' )
        raw_savedata = abs(S); %%パワー値を求める。
        sheet_number = sprintf('Sheet%d', i);
        %%xlswrite(save_xls_filename, savedata, 'Sheet1');
        baseline_savedata = mean (raw_savedata(:,1:2), 2); %%岩本変更。ベースラインの平均値を求める。-1～0秒の間
        savedata = raw_savedata - baseline_savedata; %%ベースラインコレクションを行う。
        xlswrite(save_xls_filename, savedata, sheet_number); %%Sheetには各チャネルのデータを保存する。xlswriteでエラーが出る場合がある。
        %%シート名をチャネル名に変える。
    end; %%iループのend
    sheet_number = sprintf('Sheet%d', i+1);
    xlswrite(save_xls_filename, F, sheet_number);
    sheet_number = sprintf('Sheet%d', i+2);
    %%xlswrite(save_xls_filename, T, sheet_number);
    xlswrite(save_xls_filename, T-1.0, sheet_number); %%岩本変更。時間Tからベースラインの時間1秒(２秒中１秒)を引く。
end %%jループのend

cd(oldfolder)


