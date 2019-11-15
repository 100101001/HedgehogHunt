package edu.tongji.ciwei.util;

import java.util.Iterator;
import java.util.Objects;
import java.util.function.BiConsumer;

/**
 * @author 100101001
 * @date 11/3/2019 1:36 PM
 */
public class GoodsListFunction {
    public static <E> void forEach(Iterator<E> iter, BiConsumer<Integer, ? super E> action) {
        Objects.requireNonNull(iter);
        Objects.requireNonNull(action);

        Integer idx = 0;
        while (iter.hasNext()) {
            E e = iter.next();
            action.accept(idx, e);
            idx++;
        }
    }
}
