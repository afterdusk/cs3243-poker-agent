#include <vector>
#include <random>
#include <algorithm>
#include <iterator>
#include <chrono>
#include "HandEvaluator.h"

extern "C" unsigned long long evaluate(
    unsigned long long samples, 
    unsigned char h1,
    unsigned char h2, 
    unsigned char nc, 
    char c1,
    char c2, 
    char c3,
    char c4, 
    char c5)
{
  omp::HandEvaluator evaluator;

  std::vector<int> unused;
  for (unsigned long long i = 0; i < 51; i++)
  {
    if (i == h1) continue;
    if (i == h2) continue;
    if (nc > 0 && i == c1) continue;
    if (nc > 1 && i == c2) continue;
    if (nc > 2 && i == c3) continue;
    if (nc > 3 && i == c4) continue;
    if (nc > 4 && i == c5) continue;
    unused.push_back(i);
  }
  
  int win_count = 0;
  std::default_random_engine rng(std::chrono::system_clock::now().time_since_epoch().count());
  for (int i = 0; i < samples; i++)
  {
    std::shuffle(unused.begin(), unused.end(), rng);

    int j = 0;
    int cs1 = nc > 0 ? c1 : unused[j++];
    int cs2 = nc > 1 ? c2 : unused[j++];
    int cs3 = nc > 2 ? c3 : unused[j++];
    int cs4 = nc > 3 ? c4 : unused[j++];
    int cs5 = nc > 4 ? c5 : unused[j++];
    int opp1 = unused[j++];
    int opp2 = unused[j++];

    auto player_strength = evaluator.evaluate(
        omp::Hand::empty() +
        omp::Hand(h1) +
        omp::Hand(h2) +
        omp::Hand(cs1) +
        omp::Hand(cs2) +
        omp::Hand(cs3) +
        omp::Hand(cs4) +
        omp::Hand(cs5));

    auto opp_strength = evaluator.evaluate(
        omp::Hand::empty() +
        omp::Hand(opp1) +
        omp::Hand(opp2) +
        omp::Hand(cs1) +
        omp::Hand(cs2) +
        omp::Hand(cs3) +
        omp::Hand(cs4) +
        omp::Hand(cs5));
    
    if (player_strength >= opp_strength)
    {
      win_count++;
    }
  }

  return win_count;
}
