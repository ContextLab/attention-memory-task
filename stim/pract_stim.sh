for d in ./*_F* ; do
  mkdir ${d:0:${#d}-2}

  for f in "$d" ; do
    if [[ $f = *_* ]]; then
    # for each composite in original dir
      echo ' '
      echo $f
      echo ' '
      # get object image info
      loc="$(cut -d '_' -f2 <<<"$f")"

      # find the image that shares this loc in ob_comp
      for img in ob_comp/*$loc*; do

        # mv it to the new practice dir
        mv $img ${d:0:${#d}-2}

        # move relevant object single to pract_stim_hold_out
        obj="$(cut -d '_' -f1 <<<"$img")"
        mv object_singles/*$obj* pract_stim_hold_out

      done
    fi
  done
done
