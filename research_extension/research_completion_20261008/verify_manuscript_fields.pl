use strict;
use warnings;
use JSON::PP;
use Digest::SHA qw(sha256_hex);
use FindBin;
my $d=$FindBin::Bin;
sub txt{open my $f,'<',$_[0] or die $!;local $/;return <$f>;}
my $book=decode_json(txt("$d/displayed_book_calibration.json"));
my $source=txt("$d/calibrate_displayed_book.py");
$source=~s/date=dates\.astype\('U10'\)/date=dates/;
die 'Original run script hash mismatch' unless sha256_hex($source) eq $book->{script_sha256};
open my $original,'>',"$d/calibrate_displayed_book_original_run.py" or die $!;print $original $source;close $original;
my $main=txt("$d/../../paper/Machine_Markets_JF_Submission.tex");
my $report=txt("$d/Machine_Markets_Proof_Evidence_Update_20261008.tex");
my $infer=decode_json(txt("$d/inference_completion.json"));
my @fields;
sub check{
 my($name,$value,$digits)=@_;my $literal=sprintf("%.${digits}f",$value);
 die "Missing new field $name" unless index($main,$literal)>=0 && index($report,$literal)>=0;
 push @fields,{name=>$name,value=>$value,literal=>$literal};
}
my ($obs)=grep {$_->{variant} eq 'observed'} @{$infer->{dependence}};
my ($raw)=grep {$_->{variant} eq 'raw_return'} @{$infer->{dependence}};
check('annual_observed_lower',$obs->{year_t3_95}[0],7);
check('annual_observed_upper',$obs->{year_t3_95}[1],7);
check('annual_raw_lower',$raw->{year_t3_95}[0],7);
check('annual_raw_upper',$raw->{year_t3_95}[1],7);
check('equivalence_margin',$infer->{fee}{minimum_symmetric_equivalence_margin},7);
check('relative_margin',$infer->{fee}{minimum_margin_fraction_of_benchmark},4);
check('spread_quote',$book->{pooled_metrics}{spread_quote_units}{median},4);
check('spread_bps',$book->{pooled_metrics}{spread_basis_points}{median},5);
check('buy_sweep_p90',$book->{pooled_metrics}{'buy_0.5_sweep_cost_per_reported_unit'}{p90},5);
check('sell_sweep_p90',$book->{pooled_metrics}{'sell_0.5_sweep_cost_per_reported_unit'}{p90},5);
for my $pair(['bid_L10_reported_size','19.692','19.6920'],['ask_L10_reported_size','19.171','19.1710']){
 my($key,$a,$b)=@$pair;
 die 'Depth literal missing' unless index($main,$a)>=0 && index($report,$b)>=0;
 push @fields,{name=>$key,value=>$book->{pooled_metrics}{$key}{median},main_literal=>$a,report_literal=>$b};
}
my $r={status=>'NEW_MAIN_AND_ADDENDUM_NUMERIC_FIELDS_BOUND_TO_COMPLETION_RESULTS',
 main_source_sha256=>sha256_hex($main),report_source_sha256=>sha256_hex($report),numeric_fields=>\@fields,
 original_calibration_run_script_hash_matched=>JSON::PP::true,
 current_script_change=>'Fixed-width date storage for the next run; original run script preserved exactly.',
 existing_full_empirical_check_rerun=>'see current empirical receipt bound to the exact main source'};
open my $f,'>',"$d/manuscript_completion_field_verification.json" or die $!;
print $f JSON::PP->new->canonical->pretty->encode($r);close $f;
print encode_json({status=>$r->{status},fields=>scalar @fields}),"\n";
