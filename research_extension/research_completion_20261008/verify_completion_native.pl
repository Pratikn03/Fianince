#!/usr/bin/perl
# Independent verification using signed system tools when external runtimes fail.
# NPY numeric members only: no object array or pickle is ever loaded.
use strict;
use warnings;
use JSON::PP;
use POSIX qw(strftime);
use Digest::SHA qw(sha256_hex);
use FindBin;
my $here=$FindBin::Bin;
my $root="$here/../..";
sub read_json { my ($p)=@_;open my $f,'<',$p or die $!;local $/;return decode_json(<$f>); }
sub hash_file {my($p)=@_;open my $f,'<',$p or die $!;binmode $f;my $h=Digest::SHA->new(256);$h->addfile($f);return $h->hexdigest;}
sub near {my($a,$b)=@_;die "Mismatch $a versus $b\n" if abs($a-$b)>1e-8+1e-9*abs($b);}
sub average {my($v)=@_;my $s=0;$s+=$_ for @$v;return $s/@$v;}
sub quantile {my($v,$p)=@_;my @s=sort {$a<=>$b} @$v;my $x=(@s-1)*$p;my $i=int($x);return $s[$i]+($x-$i)*($s[$i+1 > $#s ? $#s : $i+1]-$s[$i]);}
my $ip="$root/research_extension/gap_closure_20261006/cross_venue/original_panel_reproduction.json";
my $inference=read_json("$here/inference_completion.json");
die 'Input hash changed' unless hash_file($ip) eq $inference->{input_sha256};
my $rows=read_json($ip)->{rows};
for my $ref (@{$inference->{dependence}}){
 my @annual;
 for my $year (2021..2024){
  my @v=map {$_->{$ref->{variant}}{Q}} grep {$_->{year}==$year} @$rows;
  die 'Wrong annual coverage' unless @v==192;
  my $m=average(\@v);push @annual,$m;near($m,$ref->{yearly_means}{$year});
 }
 my $m=average(\@annual);my $var=0;$var+=($_-$m)**2 for @annual;$var/=3;
 my $h=3.182446305284263*sqrt($var/4);
 near($m-$h,$ref->{year_t3_95}[0]);near($m+$h,$ref->{year_t3_95}[1]);
 my $count=0;
 for my $bits (0..15){my $s=0;for my $i(0..3){$s+=(($bits>>$i)&1 ? 1 : -1)*$annual[$i];}$count++ if abs($s/4)>=abs($m)-1e-15;}
 near($count/16,$ref->{annual_sign_symmetry_reference_p});
}
my (%groups,%scores);
my @panel=grep {$_->{year}==2022} @$rows;
for my $r(@panel){my $t=$r->{symbol} eq 'BTCUSDT'?1:0;my $p=$r->{date} ge '2022-07-08'?1:0;push @{$groups{"$t$p"}},$r->{observed}{Q};}
my %means=map {$_=>average($groups{$_})} keys %groups;
my $effect=$means{'11'}-$means{'10'}-$means{'01'}+$means{'00'};
for my $r(@panel){my $t=$r->{symbol} eq 'BTCUSDT'?1:0;my $p=$r->{date} ge '2022-07-08'?1:0;my $g="$t$p";$scores{$r->{date}}+=($t==$p?1:-1)*($r->{observed}{Q}-$means{$g})/@{$groups{$g}};}
my $ss=0;$ss+=$_**2 for values %scores;
my $se=sqrt($ss*24/23*191/188);near($effect,$inference->{fee}{effect});near($se,$inference->{fee}{date_cluster_se});
my $h90=1.713871527747047* $se;
near(abs($effect)+$h90,$inference->{fee}{minimum_symmetric_equivalence_margin});
for my $row(@{$inference->{fee}{equivalence_sensitivity}}){my $passes=$row->{margin}>abs($effect)+$h90?1:0;die 'TOST decision mismatch' unless $passes==($row->{passes_5_percent_TOST}?1:0);}
my $book=read_json("$here/displayed_book_calibration.json");
my $cache=$book->{cache_path};die 'Cache hash changed' unless hash_file($cache) eq $book->{cache_sha256};
sub npy_numeric {
 my ($member,$format)=@_;
 open my $f,'-|','/usr/bin/unzip','-p',$cache,"$member.npy" or die $!;binmode $f;local $/;my $b=<$f>;close $f or die 'ZIP extraction/CRC failed';
 die 'Not NPY' unless substr($b,0,6) eq "\x93NUMPY";
 my $major=ord(substr($b,6,1));my($start,$len);
 if($major==1){$start=10;$len=unpack('v',substr($b,8,2));}
 elsif($major==2){$start=12;$len=unpack('V',substr($b,8,4));}else{die 'Unsupported NPY';}
 my $header=substr($b,$start,$len);die 'Object/Fortran member rejected' if $header=~/'descr':\s*'\|O/ or $header=~/'fortran_order':\s*True/;
 return [unpack($format,substr($b,$start+$len))];
}
my $ms=npy_numeric('ms','q<*');my $valid=npy_numeric('valid','C*');
my %data=map {$_=>npy_numeric($_,'d<*')} qw(bid_price bid_size ask_price ask_size);
my $n=@$ms;die 'Wrong minute count' unless $n==15593 && $n==$book->{selected_minutes};
# Independently confirm the selected last row of every minute against the
# already byte-authenticated original CSV, not only the newly generated cache.
my %minute_index;for my $i(0..$n-1){$minute_index{int($ms->[$i]/60000)}=$i;}
my %last_row;my $raw_rows=0;
open my $csv,'<',"$root/empirical_pipeline/data/1-09-1-20.csv" or die $!;
my $header=<$csv>;
while(my $line=<$csv>){
 die 'Unexpected CSV timestamp encoding' unless $line=~/^[^,]*,(\d+),/;
 my $minute=int($1/60000);die 'Uncovered original minute' unless exists $minute_index{$minute};
 $last_row{$minute}=$line;$raw_rows++;
}
close $csv;die 'Wrong CSV row count' unless $raw_rows==3730870;
for my $minute(keys %last_row){
 my $i=$minute_index{$minute};my @values=split(/,/,$last_row{$minute});
 die 'Wrong CSV field count' unless @values==43;die 'Selected timestamp mismatch' unless $values[1]==$ms->[$i];
 for my $j(0..9){
  die 'Bid source value mismatch' unless $values[3+2*$j]==$data{bid_price}[$i*10+$j] && $values[4+2*$j]==$data{bid_size}[$i*10+$j];
  die 'Ask source value mismatch' unless $values[23+2*$j]==$data{ask_price}[$i*10+$j] && $values[24+2*$j]==$data{ask_size}[$i*10+$j];
 }
}
my (%metrics,%day_metrics,%date_count);
for my $i(0..$n-1){
 next unless $valid->[$i];my $day=strftime('%Y-%m-%d',gmtime($ms->[$i]/1000));$date_count{$day}++;
 my @bp=@{$data{bid_price}}[$i*10..$i*10+9];my @ap=@{$data{ask_price}}[$i*10..$i*10+9];
 my @bs=@{$data{bid_size}}[$i*10..$i*10+9];my @az=@{$data{ask_size}}[$i*10..$i*10+9];
 my $mid=($bp[0]+$ap[0])/2;my $spread=$ap[0]-$bp[0];my($btotal,$atotal)=(0,0);$btotal+=$_ for @bs;$atotal+=$_ for @az;
 my %values=(spread_quote_units=>$spread,spread_basis_points=>$spread/$mid*1e4,midpoint_quote_units=>$mid,bid_L10_reported_size=>$btotal,ask_L10_reported_size=>$atotal);
 for my $side ('buy','sell'){
  my $p=$side eq 'buy'?\@ap:\@bp;my $s=$side eq 'buy'?\@az:\@bs;my $depth=$side eq 'buy'?$atotal:$btotal;
  for my $fraction (@{$book->{fractions_of_side_L10_depth}}){
   my $quantity=$fraction*$depth;my $remaining=$quantity;my $cash=0;
   for my $j(0..9){my $take=$remaining<$s->[$j]?$remaining:$s->[$j];$cash+=$take*$p->[$j];$remaining-=$take;last if $remaining<=0;}
   die 'Incomplete hypothetical sweep' if abs($remaining)>1e-9;
   my $avg=$cash/$quantity;my $cost=$side eq 'buy'?$avg-$mid:$mid-$avg;
   my $extra=$side eq 'buy'?$avg-$p->[0]:$p->[0]-$avg;
   $values{"${side}_${fraction}_sweep_cost_per_reported_unit"}=$cost;
   $values{"${side}_${fraction}_static_depth_slope"}=2*$extra/$quantity;
  }
 }
 for my $key(keys %values){push @{$metrics{$key}},$values{$key};push @{$day_metrics{$day}{$key}},$values{$key};}
}
for my $key(keys %metrics){
 my $ref=$book->{pooled_metrics}{$key};die "Unknown metric $key" unless $ref;
 near(quantile($metrics{$key},.1),$ref->{p10});near(quantile($metrics{$key},.5),$ref->{median});near(quantile($metrics{$key},.9),$ref->{p90});
 for my $row(@{$book->{daily}}){my $day=$row->{date};my $r=$row->{metrics}{$key};my $v=$day_metrics{$day}{$key};near(quantile($v,.1),$r->{p10});near(quantile($v,.5),$r->{median});near(quantile($v,.9),$r->{p90});die 'Daily count mismatch' unless $date_count{$day}==$row->{valid_minutes};}
}
my $receipt={status=>'INDEPENDENT_INFERENCE_AND_ALL_MINUTE_SWEEP_CHECKS_PASS',runtime=>'Signed macOS system Perl; core JSON/POSIX/Digest and system unzip',
 inference_sha256=>hash_file("$here/inference_completion.json"),book_sha256=>hash_file("$here/displayed_book_calibration.json"),
 verifier_sha256=>hash_file(__FILE__),scalar_sweep_records=>$n*6,pooled_metrics=>scalar(keys %metrics),daily_summaries=>scalar(keys %date_count),
 original_csv_rows_streamed=>$raw_rows,last_minute_book_rows_source_checked=>scalar(keys %last_row),object_arrays_or_pickle_loaded=>JSON::PP::false,
 limits=>'Arithmetic and declared-representation agreement; no causal identification, actual fills, dynamic impact or complete market calibration.'};
open my $out,'>',"$here/completion_evidence_verification.json" or die $!;print $out JSON::PP->new->canonical->pretty->encode($receipt);close $out;
print JSON::PP->new->canonical->pretty->encode($receipt);
